# Clipboard Monitoring Module
import platform
import threading
import time

class ClipboardMonitor:
    def __init__(self):
        self.system = platform.system()
        self.running = False
        self.clipboard_history = []
        self.thread = None
        
    def get_clipboard(self):
        """Get current clipboard content"""
        try:
            if self.system == "Windows":
                return self.get_windows_clipboard()
            elif self.system == "Linux":
                return self.get_linux_clipboard()
            elif self.system == "Darwin":
                return self.get_mac_clipboard()
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def get_windows_clipboard(self):
        """Get clipboard on Windows"""
        try:
            import win32clipboard
            
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            return {"success": True, "content": data[:1000]}
        except ImportError:
            import subprocess
            result = subprocess.run(
                ['powershell', '-command', 'Get-Clipboard'],
                capture_output=True, text=True
            )
            return {"success": True, "content": result.stdout[:1000]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_linux_clipboard(self):
        """Get clipboard on Linux"""
        try:
            import subprocess
            
            # Try xclip first
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                return {"success": True, "content": result.stdout[:1000]}
            
            # Fallback to xsel
            result = subprocess.run(
                ['xsel', '--clipboard', '--output'],
                capture_output=True, text=True
            )
            
            return {"success": True, "content": result.stdout[:1000]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mac_clipboard(self):
        """Get clipboard on macOS"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['pbpaste'],
                capture_output=True, text=True
            )
            
            return {"success": True, "content": result.stdout[:1000]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_monitoring(self, interval=5):
        """Start monitoring clipboard"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.thread.start()
        
        return {"success": True, "message": f"Clipboard monitoring started (interval: {interval}s)"}
    
    def stop_monitoring(self):
        """Stop monitoring clipboard"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        return {"success": True, "message": "Clipboard monitoring stopped"}
    
    def get_history(self, clear=True):
        """Get clipboard history"""
        history = self.clipboard_history.copy()
        if clear:
            self.clipboard_history.clear()
        
        return {"success": True, "history": history, "count": len(history)}
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop"""
        last_content = None
        
        while self.running:
            try:
                result = self.get_clipboard()
                if result["success"]:
                    content = result["content"]
                    if content and content != last_content:
                        import datetime
                        self.clipboard_history.append({
                            "timestamp": datetime.datetime.now().isoformat(),
                            "content": content[:500]
                        })
                        last_content = content
            except:
                pass
            
            time.sleep(interval)


def get_clipboard():
    """Quick clipboard get function"""
    cm = ClipboardMonitor()
    return cm.get_clipboard()


def start_clipboard_monitor(interval=5):
    """Quick clipboard monitor start function"""
    import sys
    cm = ClipboardMonitor()
    result = cm.start_monitoring(interval)
    if result["success"]:
        sys._rs_clipboard_monitor = cm
    return result


def get_clipboard_history(clear=True):
    """Quick clipboard history get function"""
    import sys
    if hasattr(sys, '_rs_clipboard_monitor'):
        return sys._rs_clipboard_monitor.get_history(clear)
    return {"success": False, "message": "Clipboard monitor not running"}
