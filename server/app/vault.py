"""
FounderOS Security Vault (AES-256-GCM Encryption)

This module provides authenticated symmetric encryption for sensitive tokens at rest, 
including third-party OAuth access tokens (Slack, Gmail, Linear) and LLM API keys (OpenAI, Gemini, Anthropic).
Uses Cryptography's AESGCM primitive with 96-bit random nonces.
"""

import base64
import logging
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("founderos.vault")

# Default 32-byte (256-bit) development key used when VAULT_SECRET_KEY is omitted
_DEV_KEY = b"founderos_secret_vault_key_32byt"


def _get_key() -> bytes:
    """
    Retrieves the 256-bit encryption key from the VAULT_SECRET_KEY environment variable.
    Falls back to the development secret key with a warning if unspecified or invalid.
    """
    key_env = os.environ.get("VAULT_SECRET_KEY")
    if key_env:
        try:
            decoded = base64.b64decode(key_env)
            if len(decoded) == 32:
                return decoded
            logger.warning("VAULT_SECRET_KEY must decode to exactly 32 bytes. Falling back to dev key.")
        except Exception:
            logger.warning("Invalid base64 in VAULT_SECRET_KEY. Falling back to dev key.")

    logger.info("Using development secret key for AES-256-GCM vault.")
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
    
    Returns:
        Original decrypted plain text string, or empty string on authentication failure.
    """
    if not cipher_text:
        return ""
    try:
        key = _get_key()
        data = base64.b64decode(cipher_text.encode("utf-8"))
        if len(data) < 12:
            return ""
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt vault token: {e}")
        return ""
