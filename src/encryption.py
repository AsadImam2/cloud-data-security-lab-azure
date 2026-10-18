import os
import json
import base64
from key_manager import load_manifest, get_key
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEY_DIR = PROJECT_ROOT / "keys"
DATA_DIR = PROJECT_ROOT / "data" / "encrypted"

KEY_FILE = KEY_DIR / "demo_key_v1.key"
ENCRYPTED_FILE = DATA_DIR / "sample.enc"


def load_or_create_key():
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    if KEY_FILE.exists():
        key = KEY_FILE.read_bytes()

        if len(key) != 32:
            raise ValueError("AES-256 key must contain exactly 32 bytes.")

        return key

    key = AESGCM.generate_key(bit_length=256)

    with KEY_FILE.open("xb") as file:
        file.write(key)

    return key


def encrypt_data(plaintext, key,key_id="demo_key_v1"):
    aesgcm = AESGCM(key)

    # A fresh, random 12-byte nonce is generated for each encryption.
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return {
        "algorithm": "AES-256-GCM",
        "key_id": key_id,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_data(encrypted_record, key):
    if encrypted_record.get("algorithm") != "AES-256-GCM":
        raise ValueError("Unsupported encryption algorithm.")

    nonce = base64.b64decode(encrypted_record["nonce"], validate=True)
    ciphertext = base64.b64decode(
        encrypted_record["ciphertext"],
        validate=True,
    )

    if len(nonce) != 12:
        raise ValueError("Invalid AES-GCM nonce length.")

    aesgcm = AESGCM(key)

    # Authentication fails if the ciphertext or authentication tag is changed.
    return aesgcm.decrypt(nonce, ciphertext, None)

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sample_data = {
        "record_id": "SEC-002",
        "classification": "Confidential",
        "message": "This is fictional data encrypted with the active key.",
    }

    plaintext = json.dumps(sample_data).encode("utf-8")

    # Read the current active key ID from the manifest.
    manifest = load_manifest()
    active_key_id = manifest["active_key_id"]

    if not active_key_id:
        raise RuntimeError("No active encryption key is configured.")

    # Retrieve the matching key from the key manager.
    key = get_key(active_key_id)

    encrypted_record = encrypt_data(
        plaintext,
        key,
        key_id=active_key_id,
    )

    # Save the encrypted record separately, preserving sample.enc.
    encrypted_file = DATA_DIR / "sample_v2.enc"

    with encrypted_file.open("w", encoding="utf-8") as file:
        json.dump(encrypted_record, file, indent=2)

    print("Encryption successful.")
    print(f"Algorithm: {encrypted_record['algorithm']}")
    print(f"Key ID: {encrypted_record['key_id']}")
    print(f"Encrypted file: {encrypted_file}")

    # Verify decryption using the same key.
    with encrypted_file.open("r", encoding="utf-8") as file:
        stored_record = json.load(file)

    decryption_key = get_key(stored_record["key_id"])
    recovered_plaintext = decrypt_data(stored_record, decryption_key)

    if recovered_plaintext == plaintext:
        print("Verification passed: decrypted data matches original.")
    else:
        raise RuntimeError("Decryption verification failed.")


if __name__ == "__main__":
    main()
