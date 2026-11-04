# Geolocation Module
import platform
import socket
import json
import urllib.request
from pathlib import Path

def get_geolocation():
    """Get geolocation using multiple methods"""
    results = {}
    
    # Method 1: IP-based geolocation
    results["ip_geolocation"] = get_ip_geolocation()
    
    # Method 2: System location (if available)
    results["system_location"] = get_system_location()
    
    # Method 3: WiFi-based location
    results["wifi_location"] = get_wifi_location()
    
    # Method 4: GPS (if available)
    results["gps_location"] = get_gps_location()
    
    return results


def get_ip_geolocation():
    """Get location based on public IP"""
    try:
        # Get public IP
        with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5) as response:
            public_ip = json.loads(response.read().decode())['ip']
        
        # Get geolocation from IP
        with urllib.request.urlopen(f'https://ipapi.co/{public_ip}/json/', timeout=5) as response:
            location = json.loads(response.read().decode())
        
        return {
            "success": True,
            "ip": public_ip,
            "city": location.get('city'),
            "region": location.get('region'),
            "country": location.get('country_name'),
            "country_code": location.get('country_code'),
            "latitude": location.get('latitude'),
            "longitude": location.get('longitude'),
            "timezone": location.get('timezone'),
            "isp": location.get('org'),
            "asn": location.get('asn')
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_system_location():
    """Get location from system settings"""
    system = platform.system()
    
    try:
        if system == "Windows":
            return get_windows_location()
        elif system == "Darwin":
            return get_mac_location()
        elif system == "Linux":
            return get_linux_location()
    except Exception as e:
        pass
    
    return {"success": False, "message": "No system location found"}


def get_windows_location():
    """Get location from Windows registry/settings"""
    try:
        import winreg
        
        # Check Windows location settings
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "Value")
        winreg.CloseKey(key)
        
        return {"success": True, "location_enabled": value == "Allow"}
    except:
        return {"success": False, "message": "Could not read Windows location settings"}


def get_mac_location():
    """Get location from macOS CoreLocation"""
    try:
        import subprocess
        
        # Try to get location from system preferences
        result = subprocess.run(
            ['defaults', 'read', 'com.apple.locationd', 'LocationServicesEnabled'],
            capture_output=True, text=True
        )
        
        return {"success": True, "location_enabled": "1" in result.stdout}
    except:
        return {"success": False, "message": "Could not read macOS location settings"}


def get_linux_location():
    """Get location from Linux system"""
    try:
        import subprocess
        
        # Try geoclue2 or other location services
        result = subprocess.run(
            ['geoiplookup', socket.gethostbyname(socket.gethostname())],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return {"success": True, "geoip": result.stdout.strip()}
    except:
        pass
    
    return {"success": False, "message": "No Linux location service found"}


def get_wifi_location():
    """Get location based on nearby WiFi networks"""
    system = platform.system()
    
    try:
        if system == "Linux":
            return get_linux_wifi_location()
        elif system == "Windows":
            return get_windows_wifi_location()
        elif system == "Darwin":
            return get_mac_wifi_location()
    except Exception as e:
        pass
    
    return {"success": False, "message": "Could not get WiFi location"}


def get_linux_wifi_location():
    """Get WiFi networks on Linux"""
    try:
        import subprocess
        
        # Try nmcli (NetworkManager)
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL', 'dev', 'wifi', 'list'],
            capture_output=True, text=True
        )
        
        networks = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(':')
                if len(parts) >= 3:
                    networks.append({
                        "ssid": parts[0],
                        "bssid": parts[1],
                        "signal": parts[2]
                    })
        
        return {"success": True, "networks": networks[:10]}  # Top 10
    except:
        return {"success": False, "message": "NetworkManager not available"}


def get_windows_wifi_location():
    """Get WiFi networks on Windows"""
    try:
        import subprocess
        
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True, text=True
        )
        
        return {"success": True, "raw_output": result.stdout[:2000]}
    except:
        return {"success": False, "message": "Could not get WiFi networks"}


def get_mac_wifi_location():
    """Get WiFi networks on macOS"""
    try:
        import subprocess
        
        result = subprocess.run(
            ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
            capture_output=True, text=True
        )
        
        return {"success": True, "raw_output": result.stdout[:2000]}
    except:
        return {"success": False, "message": "Could not get WiFi networks"}


def get_gps_location():
    """Get GPS location if available"""
    try:
        import subprocess
        
        # Try GPSD on Linux
        result = subprocess.run(
            ['cat', '/var/run/gpsd/gps'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return {"success": True, "gps_data": result.stdout[:500]}
    except:
        pass
    
    return {"success": False, "message": "No GPS device found"}


def get_network_info():
    """Get detailed network information"""
    import socket
    
    info = {
        "hostname": socket.gethostname(),
        "local_ip": socket.gethostbyname(socket.gethostname()),
        "fqdn": socket.getfqdn()
    }
    
    try:
        # Get all network interfaces
        import subprocess
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        info["interfaces"] = result.stdout[:2000]
    except:
        pass
    
    return {"success": True, "info": info}


def generate_webrtc_html():
    """Generate HTML for WebRTC geolocation"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebRTC Geolocation</title>
        <script>
            function getWebRTCIPs() {
                return new Promise((resolve) => {
                    const ips = [];
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        navigator.mediaDevices.getUserMedia({ audio: true, video: false })
                            .then(stream => {
                                const pc = new RTCPeerConnection({ iceServers: [] });
                                pc.createDataChannel("");
                                pc.addTrack(stream.getAudioTracks()[0]);
                                pc.createOffer().then(offer => pc.setLocalDescription(offer));
                                
                                pc.onicecandidate = e => {
                                    if (e.candidate) {
                                        const match = e.candidate.candidate.match(/([0-9]{1,3}\\.){3}[0-9]{1,3}/g);
                                        if (match) ips.push(...match);
                                    } else {
                                        setTimeout(() => {
                                            resolve([...new Set(ips)]);
                                        }, 1000);
                                    }
                                };
                            })
                            .catch(err => resolve(ips));
                    } else {
                        resolve(ips);
                    }
                });
            }
            
            window.onload = async () => {
                const ips = await getWebRTCIPs();
                document.getElementById('result').innerHTML = JSON.stringify(ips, null, 2);
            };
        </script>
    </head>
    <body>
        <h1>WebRTC IP Discovery</h1>
        <pre id="result">Discovering IPs...</pre>
    </body>
    </html>
    '''
