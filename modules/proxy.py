# Proxy Module
import socket
import urllib.request
import urllib.error
import json

class ProxyManager:
    def __init__(self, proxy_url: str = None):
        self.proxy_url = proxy_url
        self.proxies = {}
        self.current_proxy = None
        
    def set_proxy(self, proxy_url: str):
        """Set the proxy to use"""
        self.proxy_url = proxy_url
        self.current_proxy = proxy_url
        
        # Parse proxy URL
        if proxy_url:
            if proxy_url.startswith('http://') or proxy_url.startswith('https://'):
                self.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            elif proxy_url.startswith('socks5://') or proxy_url.startswith('socks4://'):
                self.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
        
        return {"success": True, "message": f"Proxy set: {proxy_url}"}
    
    def clear_proxy(self):
        """Clear current proxy"""
        self.proxy_url = None
        self.current_proxy = None
        self.proxies = {}
        return {"success": True, "message": "Proxy cleared"}
    
    def get_proxy(self):
        """Get current proxy"""
        return {"success": True, "proxy": self.current_proxy}
    
    def test_proxy(self):
        """Test if proxy is working"""
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(self.proxies))
            urllib.request.install_opener(opener)
            
            # Test by checking IP
            response = urllib.request.urlopen('https://api.ipify.org?format=json', timeout=10)
            ip_data = json.loads(response.read().decode())
            
            return {
                "success": True,
                "working": True,
                "ip": ip_data['ip'],
                "proxy": self.current_proxy
            }
        except Exception as e:
            return {
                "success": True,
                "working": False,
                "error": str(e),
                "proxy": self.current_proxy
            }
    
    def get_open_url(self):
        """Get opener with proxy configured"""
        return urllib.request.build_opener(urllib.request.ProxyHandler(self.proxies))


def check_proxychains():
    """Check if proxychains is installed"""
    import subprocess
    
    try:
        result = subprocess.run(['which', 'proxychains'], capture_output=True, text=True)
        if result.returncode == 0:
            return {"installed": True, "path": result.stdout.strip()}
        return {"installed": False}
    except:
        return {"installed": False}


def run_with_proxychains(command: str):
    """Run a command with proxychains"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['proxychains', '-q'] + command.split(),
            capture_output=True, text=True, timeout=60
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rotate_proxy(proxy_list: list):
    """Rotate through a list of proxies"""
    import random
    
    proxy = random.choice(proxy_list)
    pm = ProxyManager(proxy)
    return pm.test_proxy()


def check_proxy_anonymity(proxy_url: str):
    """Check proxy anonymity level"""
    try:
        import urllib.request
        import http.client
        
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url}))
        urllib.request.install_opener(opener)
        
        # Check if proxy reveals original IP
        conn = http.client.HTTPConnection('httpbin.org', timeout=10)
        conn.request('GET', '/headers')
        response = conn.getresponse()
        headers = json.loads(response.read().decode())
        
        # Analyze headers
        anonymity = "Transparent"
        if 'X-Forwarded-For' not in headers.get('headers', {}):
            anonymity = "Anonymous"
        if 'Via' not in headers.get('headers', {}):
            anonymity = "Elite"
        
        return {
            "success": True,
            "anonymity": anonymity,
            "headers": headers.get('headers', {}),
            "ip": headers.get('origin', 'Unknown')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Global proxy manager
proxy_manager = ProxyManager()
