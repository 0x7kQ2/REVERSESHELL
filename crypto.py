# Cryptography Module for Encrypted Communication
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import config

def derive_key(password: bytes, salt: bytes = b"REVERSESHELL_SALT") -> bytes:
    """Derive a 32-byte key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def get_cipher() -> Fernet:
    """Get Fernet cipher for encryption/decryption"""
    key = derive_key(config.ENCRYPTION_KEY)
    return Fernet(key)

def encrypt(data: bytes) -> str:
    """Encrypt data and return base64 string"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(data)
    return base64.b64encode(encrypted).decode()

def decrypt(data: str) -> bytes:
    """Decrypt base64 string and return bytes"""
    cipher = get_cipher()
    encrypted = base64.b64decode(data)
    return cipher.decrypt(encrypted)

def hash_file(filepath: str) -> str:
    """Get SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()
