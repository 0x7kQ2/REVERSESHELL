# Network Sniffing Module
import platform
import subprocess
import json
import socket
import struct
from pathlib import Path

class NetworkSniffer:
    def __init__(self):
        self.system = platform.system()
        self.packets = []
        
    def sniff(self, count=100, interface=None):
        """Sniff network packets"""
        try:
            if self.system == "Linux":
                return self.sniff_linux(count, interface)
            elif self.system == "Windows":
                return self.sniff_windows(count)
            elif self.system == "Darwin":
                return self.sniff_mac(count)
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def sniff_linux(self, count=100, interface=None):
        """Sniff packets on Linux using tcpdump"""
        try:
            if not interface:
                # Get default interface
                result = subprocess.run(
                    ['ip', 'route', 'get', '1'],
                    capture_output=True, text=True
                )
                parts = result.stdout.split()
                for i, part in enumerate(parts):
                    if part == 'dev':
                        interface = parts[i + 1]
                        break
            
            if not interface:
                interface = 'eth0'
            
            # Run tcpdump
            cmd = ['tcpdump', '-i', interface, '-c', str(count), '-n', '-s', '1000']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "success": True,
                "interface": interface,
                "packets": result.stdout[:5000]
            }
        except FileNotFoundError:
            return {"success": False, "message": "tcpdump not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sniff_windows(self, count=100):
        """Sniff packets on Windows"""
        try:
            # Try tcpdump or WinPcap
            cmd = ['tcpdump', '-c', str(count), '-n']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "success": True,
                "packets": result.stdout[:5000]
            }
        except FileNotFoundError:
            return {"success": False, "message": "tcpdump not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sniff_mac(self, count=100):
        """Sniff packets on macOS"""
        try:
            cmd = ['tcpdump', '-c', str(count), '-n']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "success": True,
                "packets": result.stdout[:5000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_network_info(self):
        """Get detailed network information"""
        try:
            info = {
                "hostname": socket.gethostname(),
                "interfaces": self.get_interfaces(),
                "arp_table": self.get_arp_table(),
                "routing_table": self.get_routing_table(),
                "open_ports": self.get_open_ports()
            }
            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_interfaces(self):
        """Get network interface information"""
        try:
            interfaces = []
            
            if self.system == "Linux":
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
                interfaces.append(result.stdout[:3000])
            elif self.system == "Windows":
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                interfaces.append(result.stdout[:3000])
            elif self.system == "Darwin":
                result = subprocess.run(['ifconfig', '-a'], capture_output=True, text=True)
                interfaces.append(result.stdout[:3000])
            
            return interfaces
        except Exception as e:
            return [str(e)]
    
    def get_arp_table(self):
        """Get ARP table"""
        try:
            if self.system == "Linux":
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            elif self.system == "Windows":
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            elif self.system == "Darwin":
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            else:
                return []
            
            return result.stdout[:3000]
        except Exception as e:
            return str(e)
    
    def get_routing_table(self):
        """Get routing table"""
        try:
            if self.system == "Linux":
                result = subprocess.run(['route', '-n'], capture_output=True, text=True)
            elif self.system == "Windows":
                result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            elif self.system == "Darwin":
                result = subprocess.run(['netstat', '-rn'], capture_output=True, text=True)
            else:
                return []
            
            return result.stdout[:3000]
        except Exception as e:
            return str(e)
    
    def get_open_ports(self):
        """Get open ports"""
        try:
            if self.system == "Linux":
                result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            elif self.system == "Windows":
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            elif self.system == "Darwin":
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            else:
                return []
            
            return result.stdout[:3000]
        except Exception as e:
            return str(e)
    
    def scan_network(self, target_network: str):
        """Scan a network for hosts"""
        try:
            import nmap
            
            nm = nmap.PortScanner()
            nm.scan(hosts=target_network, arguments='-sn')
            
            hosts = []
            for host in nm.all_hosts():
                hosts.append({
                    "ip": host,
                    "hostname": nm[host].hostname(),
                    "state": nm[host].state()
                })
            
            return {"success": True, "hosts": hosts}
        except ImportError:
            # Fallback to ping scan
            import ipaddress
            
            hosts = []
            try:
                network = ipaddress.ip_network(target_network)
                for ip in network.hosts()[:25]:  # Scan first 25 hosts
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', str(ip)],
                        capture_output=True, timeout=2
                    )
                    if result.returncode == 0:
                        hosts.append({"ip": str(ip), "alive": True})
            except:
                pass
            
            return {"success": True, "hosts": hosts}
    
    def extract_creds_from_traffic(self, packet_data: str):
        """Extract credentials from captured traffic"""
        creds = []
        
        # Look for common credential patterns
        import re
        
        patterns = [
            (r'password[=":\']?\s*([^\s&"]+)', 'password'),
            (r'passwd[=":\']?\s*([^\s&"]+)', 'passwd'),
            (r'pwd[=":\']?\s*([^\s&"]+)', 'pwd'),
            (r'auth[=":\']?\s*([^\s&"]+)', 'auth'),
            (r'credentials?[=":\']?\s*([^\s&"]+)', 'credentials'),
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, packet_data, re.IGNORECASE)
            for match in matches:
                creds.append({
                    "type": name,
                    "value": match[:50]
                })
        
        return {"success": True, "credentials": creds}


def sniff_packets(count=100):
    """Quick packet sniff function"""
    sniffer = NetworkSniffer()
    return sniffer.sniff(count)


def get_network_info():
    """Quick network info function"""
    sniffer = NetworkSniffer()
    return sniffer.get_network_info()
