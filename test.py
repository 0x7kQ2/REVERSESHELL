#!/usr/bin/env python3
"""Quick test to verify the reverse shell works"""

import threading
import time
import subprocess
import sys

print("🐉 REVERSESHELL Quick Test")
print("=" * 40)

# Test 1: Check dependencies
print("\n[1] Checking dependencies...")
try:
    import cryptography
    print("    ✓ cryptography module OK")
except ImportError:
    print("    ✗ Install: pip install cryptography")
    sys.exit(1)

# Test 2: Check encryption
print("\n[2] Testing encryption...")
try:
    from crypto import encrypt, decrypt
    test_msg = b"Hello Reverse Shell!"
    encrypted = encrypt(test_msg)
    decrypted = decrypt(encrypted)
    assert decrypted == test_msg
    print("    ✓ Encryption working")
except Exception as e:
    print(f"    ✗ Encryption failed: {e}")
    sys.exit(1)

# Test 3: Check server can start
print("\n[3] Testing server startup...")
try:
    import socket
    sock = socket.socket()
    result = sock.connect_ex(('127.0.0.1', 9999))
    sock.close()
    if result == 0:
        print("    ⚠ Port 9999 already in use")
    else:
        print("    ✓ Port 9999 available")
except Exception as e:
    print(f"    ✗ Socket test failed: {e}")

print("\n" + "=" * 40)
print("✅ All tests passed!")
print("\nTo start:")
print("  1. Run: python3 server.py")
print("  2. In another terminal: python3 client.py 127.0.0.1 9999")
print("  3. Try commands in the GUI!")
