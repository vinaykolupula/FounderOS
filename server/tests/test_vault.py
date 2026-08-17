import unittest
import os
from app.vault import encrypt_token, decrypt_token, _get_key


class TestVaultEncryption(unittest.TestCase):
    """Function-to-function tests for AES-256-GCM authenticated vault encryption."""

    def test_get_vault_key(self):
        key = _get_key()
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 32)  # 256 bits

    def test_encrypt_and_decrypt_standard_api_key(self):
        plain_key = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
        encrypted = encrypt_token(plain_key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, plain_key)

        decrypted = decrypt_token(encrypted)
        self.assertEqual(decrypted, plain_key)

    def test_empty_and_whitespace_token(self):
        self.assertEqual(encrypt_token(""), "")
        self.assertEqual(decrypt_token(""), "")
        self.assertEqual(encrypt_token(None), "")
        self.assertEqual(decrypt_token(None), "")

    def test_tampered_ciphertext_fails_gracefully(self):
        plain = "sensitive-anthropic-key-abc"
        encrypted = encrypt_token(plain)
        # Corrupt the ciphertext
        tampered = encrypted[:-4] + "XXXX"
        decrypted = decrypt_token(tampered)
        self.assertEqual(decrypted, "")

    def test_unicode_and_special_characters(self):
        plain = "sk-🔑-test-token-ünicode-!@#$%^&*()"
        encrypted = encrypt_token(plain)
        decrypted = decrypt_token(encrypted)
        self.assertEqual(decrypted, plain)


if __name__ == "__main__":
    unittest.main()
