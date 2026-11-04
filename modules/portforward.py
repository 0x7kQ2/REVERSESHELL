# Port Forwarding / Tunneling Module
import socket
import threading
import json

class PortForwarder:
    def __init__(self, local_port: int, remote_host: str, remote_port: int):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.running = False
        self.server = None
        self.connections = []
        
    def start(self):
        """Start port forwarding"""
        try:
            self.running = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('127.0.0.1', self.local_port))
            self.server.listen(5)
            
            threading.Thread(target=self._accept_loop, daemon=True).start()
            
            return {
                "success": True,
                "message": f"Forwarding localhost:{self.local_port} -> {self.remote_host}:{self.remote_port}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop(self):
        """Stop port forwarding"""
        self.running = False
        if self.server:
            self.server.close()
        return {"success": True, "message": "Port forwarding stopped"}
    
    def _accept_loop(self):
        """Accept incoming connections"""
        while self.running:
            try:
                self.server.settimeout(1)
                client, addr = self.server.accept()
                threading.Thread(target=self._handle_connection, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_connection(self, client):
        """Handle a single connection"""
        try:
            # Connect to remote
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((self.remote_host, self.remote_port))
            
            # Forward data both ways
            threading.Thread(target=self._forward, args=(client, remote), daemon=True).start()
            threading.Thread(target=self._forward, args=(remote, client), daemon=True).start()
            
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            client.close()
    
    def _forward(self, from_sock, to_sock):
        """Forward data from one socket to another"""
        while self.running:
            try:
                data = from_sock.recv(4096)
                if not data:
                    break
                to_sock.sendall(data)
            except:
                break


class SOCKSProxy:
    def __init__(self, port: int = 1080):
        self.port = port
        self.running = False
        self.server = None
        
    def start(self):
        """Start SOCKS proxy"""
        try:
            self.running = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('127.0.0.1', self.port))
            self.server.listen(5)
            
            threading.Thread(target=self._accept_loop, daemon=True).start()
            
            return {"success": True, "message": f"SOCKS proxy started on port {self.port}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop(self):
        """Stop SOCKS proxy"""
        self.running = False
        if self.server:
            self.server.close()
        return {"success": True, "message": "SOCKS proxy stopped"}
    
    def _accept_loop(self):
        """Accept SOCKS connections"""
        while self.running:
            try:
                self.server.settimeout(1)
                client, addr = self.server.accept()
                threading.Thread(target=self._handle_socks, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
    
    def _handle_socks(self, client):
        """Handle SOCKS connection"""
        try:
            # Read SOCKS request
            data = client.recv(1024)
            
            # Simple response (would need proper SOCKS implementation)
            client.sendall(b'\x05\x00')  # SOCKS5 response
            
        except Exception as e:
            print(f"SOCKS error: {e}")
        finally:
            client.close()


def forward_port(local_port: int, remote_host: str, remote_port: int):
    """Quick port forward function"""
    pf = PortForwarder(local_port, remote_host, remote_port)
    return pf.start()


def start_socks(port: int = 1080):
    """Quick SOCKS proxy function"""
    sp = SOCKSProxy(port)
    return sp.start()
