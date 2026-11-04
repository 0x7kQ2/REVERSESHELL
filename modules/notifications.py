# Notification Monitoring Module
import platform
import subprocess
import threading
import time
import json
from pathlib import Path

class NotificationMonitor:
    def __init__(self):
        self.system = platform.system()
        self.notifications = []
        self.running = False
        self.thread = None
        
    def get_notifications(self):
        """Get current notifications"""
        try:
            if self.system == "Linux":
                return self.get_linux_notifications()
            elif self.system == "Windows":
                return self.get_windows_notifications()
            elif self.system == "Darwin":
                return self.get_mac_notifications()
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def get_linux_notifications(self):
        """Get notifications on Linux"""
        try:
            # Check for notification daemon
            result = subprocess.run(
                ['dbus-send', '--session', '--dest=org.freedesktop.Notifications',
                 '--type=method_call', '/org/freedesktop/Notifications',
                 'org.freedesktop.Notifications.GetCapabilities'],
                capture_output=True, text=True
            )
            
            return {
                "success": True,
                "capabilities": result.stdout[:500]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_windows_notifications(self):
        """Get notifications on Windows"""
        try:
            # Check Windows Action Center
            result = subprocess.run(
                ['powershell', '-command', 'Get-EventLog -LogName Application -Newest 20'],
                capture_output=True, text=True
            )
            
            return {
                "success": True,
                "events": result.stdout[:2000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mac_notifications(self):
        """Get notifications on macOS"""
        try:
            # Check notification log
            result = subprocess.run(
                ['log', 'show', '--predicate', 'eventMessage contains "notification"',
                 '--last', '1h'],
                capture_output=True, text=True
            )
            
            return {
                "success": True,
                "notifications": result.stdout[:2000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_monitoring(self, interval: int = 5):
        """Start monitoring notifications"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.thread.start()
        
        return {"success": True, "message": f"Notification monitoring started (interval: {interval}s)"}
    
    def stop_monitoring(self):
        """Stop monitoring notifications"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        return {"success": True, "message": "Notification monitoring stopped"}
    
    def get_history(self, clear: bool = True):
        """Get notification history"""
        history = self.notifications.copy()
        if clear:
            self.notifications.clear()
        
        return {"success": True, "history": history, "count": len(history)}
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop"""
        while self.running:
            try:
                result = self.get_notifications()
                if result["success"]:
                    import datetime
                    self.notifications.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "data": result
                    })
            except:
                pass
            
            time.sleep(interval)


class WindowMonitor:
    def __init__(self):
        self.system = platform.system()
        self.windows = []
        
    def get_active_window(self):
        """Get currently active window"""
        try:
            if self.system == "Linux":
                return self.get_linux_active_window()
            elif self.system == "Windows":
                return self.get_windows_active_window()
            elif self.system == "Darwin":
                return self.get_mac_active_window()
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def get_linux_active_window(self):
        """Get active window on Linux"""
        try:
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True, text=True
            )
            
            return {
                "success": True,
                "title": result.stdout.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_windows_active_window(self):
        """Get active window on Windows"""
        try:
            import pywin32
        
            import win32gui
            import win32ui
            
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            return {
                "success": True,
                "title": title,
                "hwnd": hwnd
            }
        except ImportError:
            result = subprocess.run(
                ['powershell', '-command', '[System.Windows.Forms.SendKeys]::SendWait("{TAB}")'],
                capture_output=True, text=True
            )
            
            return {"success": True, "title": "Unknown"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mac_active_window(self):
        """Get active window on macOS"""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell app "System Events" to get name of first window of first process whose frontmost is true'],
                capture_output=True, text=True
            )
            
            return {
                "success": True,
                "title": result.stdout.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_all_windows(self):
        """List all open windows"""
        try:
            if self.system == "Linux":
                result = subprocess.run(
                    ['xwininfo', '-root', '-tree'],
                    capture_output=True, text=True
                )
            elif self.system == "Windows":
                result = subprocess.run(
                    ['tasklist'],
                    capture_output=True, text=True
                )
            elif self.system == "Darwin":
                result = subprocess.run(
                    ['osascript', '-e', 'tell app "System Events" to get name of every process whose frontmost is true'],
                    capture_output=True, text=True
                )
            
            return {
                "success": True,
                "windows": result.stdout[:3000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def get_notifications():
    """Quick notification get function"""
    nm = NotificationMonitor()
    return nm.get_notifications()


def get_active_window():
    """Quick active window get function"""
    wm = WindowMonitor()
    return wm.get_active_window()
