"""
FounderOS Security Vault (AES-256-GCM Encryption)

This module provides authenticated symmetric encryption for sensitive tokens at rest, 
including third-party OAuth access tokens (Slack, Gmail, Linear) and LLM API keys (OpenAI, Gemini, Anthropic).
Uses Cryptography's AESGCM primitive with 96-bit random nonces.
"""

import base64
import logging
import os
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("founderos.vault")

# Legacy 32-byte development key used strictly as backward-compatible fallback in development
_DEV_KEY = b"founderos_secret_vault_key_32byt"


def _get_key() -> bytes:
    """
    Retrieves the 256-bit encryption key.
    
    1. In production (ENVIRONMENT=production/prod):
       Strictly enforces that VAULT_SECRET_KEY is defined and exactly 32 bytes;
       fails fast with RuntimeError if missing or malformed.
       
    2. In non-production:
       Checks VAULT_SECRET_KEY environment variable.
       If unset, checks for a persistent local .vault_key file (mode 0600).
       If absent, generates a cryptographically secure 32-byte key (os.urandom(32)),
       persists it locally with 0600 permissions, and uses it.
    """
    key_env = os.environ.get("VAULT_SECRET_KEY")
    env_name = os.environ.get("ENVIRONMENT", "development").lower().strip()
    is_prod = env_name in ["production", "prod"]

    if key_env:
        try:
            decoded = base64.b64decode(key_env)
            if len(decoded) == 32:
                return decoded
            msg = "VAULT_SECRET_KEY must decode to exactly 32 bytes (256 bits)."
            if is_prod:
                raise RuntimeError(f"CRITICAL SECURITY ERROR: {msg}")
            logger.warning(f"{msg} Falling back to secure local key file.")
        except Exception as e:
            if is_prod:
                raise RuntimeError(f"CRITICAL SECURITY ERROR: Invalid base64 in VAULT_SECRET_KEY: {e}")
            logger.warning(f"Invalid base64 in VAULT_SECRET_KEY: {e}. Falling back to secure local key file.")

    if is_prod:
        raise RuntimeError("CRITICAL SECURITY ERROR: VAULT_SECRET_KEY environment variable must be set in production mode.")

    # In local development / testing: manage secure local key file
    try:
        # Check both server root and project root
        app_dir = Path(__file__).resolve().parent
        server_dir = app_dir.parent
        project_dir = server_dir.parent
        
        # Prefer existing .vault_key
        key_candidates = [server_dir / ".vault_key", project_dir / ".vault_key"]
        for cand in key_candidates:
            if cand.exists():
                try:
                    stored_b64 = cand.read_text(encoding="utf-8").strip()
                    decoded = base64.b64decode(stored_b64)
                    if len(decoded) == 32:
                        return decoded
                except Exception as ex:
                    logger.warning(f"Failed to load key from {cand}: {ex}")

        # If not found, generate a fresh secure 256-bit key
        new_key = os.urandom(32)
        target_file = server_dir / ".vault_key"
        target_file.write_text(base64.b64encode(new_key).decode("utf-8"), encoding="utf-8")
        try:
            os.chmod(target_file, 0o600)
        except OSError:
            pass  # Windows or restricted filesystem
        logger.info(f"Generated secure local vault key in {target_file} (mode 0600)")
        return new_key
    except Exception as e:
        logger.warning(f"Unable to manage local .vault_key: {e}. Falling back to dev key.")
        return _DEV_KEY


def encrypt_token(plain_text: Optional[str]) -> str:
    """
    Encrypts a plain text secret string using AES-256-GCM.
    
    Returns:
        Base64-encoded string combining 12-byte random nonce + ciphertext.
    """
    if not plain_text:
        return ""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit random GCM nonce
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_token(cipher_text: Optional[str]) -> str:
    """
    Decrypts a base64-encoded nonce + ciphertext payload back into plain text.
    Includes backward-compatible fallback for ciphertexts encrypted under legacy dev key.
    
    Returns:
        Original decrypted plain text string, or empty string on authentication failure.
    """
    if not cipher_text:
        return ""
    try:
        data = base64.b64decode(cipher_text.encode("utf-8"))
        if len(data) < 12:
            return ""
        nonce = data[:12]
        ciphertext = data[12:]
        
        # 1. Attempt decryption with active key
        key = _get_key()
        aesgcm = AESGCM(key)
        try:
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode("utf-8")
        except Exception:
            # 2. Backward compatibility fallback in non-production
            is_prod = os.environ.get("ENVIRONMENT", "development").lower().strip() in ["production", "prod"]
            if not is_prod and key != _DEV_KEY:
                try:
                    fallback_aes = AESGCM(_DEV_KEY)
                    decrypted = fallback_aes.decrypt(nonce, ciphertext, None)
                    return decrypted.decode("utf-8")
                except Exception:
                    pass
            raise
    except Exception as e:
        logger.error(f"Failed to decrypt vault token: {e}")
        return ""
