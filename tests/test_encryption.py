import sys
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from encryption import encrypt_data, decrypt_data


def test_encrypt_then_decrypt():
    key = AESGCM.generate_key(bit_length=256)
    plaintext = b"Fictional confidential test data"

    encrypted = encrypt_data(plaintext, key)
    recovered = decrypt_data(encrypted, key)

    assert recovered == plaintext


def test_modified_ciphertext_is_rejected():
    key = AESGCM.generate_key(bit_length=256)
    plaintext = b"Test data for tampering detection"

    encrypted = encrypt_data(plaintext, key)
    tampered = encrypted.copy()

    ciphertext = tampered["ciphertext"]
    replacement = "A" if ciphertext[0] != "A" else "B"
    tampered["ciphertext"] = replacement + ciphertext[1:]

    with pytest.raises(InvalidTag):
        decrypt_data(tampered, key)


def test_wrong_key_is_rejected():
    key1 = AESGCM.generate_key(bit_length=256)
    key2 = AESGCM.generate_key(bit_length=256)

    encrypted = encrypt_data(b"Secret test data", key1)

    with pytest.raises(InvalidTag):
        decrypt_data(encrypted, key2)


def test_fresh_nonce_is_generated():
    key = AESGCM.generate_key(bit_length=256)
    plaintext = b"Same plaintext for two encryption operations"

    encrypted1 = encrypt_data(plaintext, key)
    encrypted2 = encrypt_data(plaintext, key)

    assert encrypted1["nonce"] != encrypted2["nonce"]
