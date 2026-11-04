# Screenshot Module
import platform
import base64
import io
from pathlib import Path

def capture_screenshot(quality=85):
    """Capture screenshot on any platform"""
    system = platform.system()
    
    try:
        if system == "Linux":
            return capture_linux_screenshot(quality)
        elif system == "Windows":
            return capture_windows_screenshot(quality)
        elif system == "Darwin":
            return capture_mac_screenshot(quality)
        else:
            return {"success": False, "message": f"Unsupported platform: {system}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def capture_linux_screenshot(quality=85):
    """Capture screenshot on Linux using PIL"""
    try:
        from PIL import ImageGrab, Image
        import subprocess
        
        # Try to get display
        try:
            display = subprocess.check_output("xrandr | grep ' connected' | awk '{print $1}'", shell=True).decode().strip()
        except:
            display = ":0"
        
        # Capture screenshot
        img = ImageGrab.grab()
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode()
        
        return {
            "success": True,
            "format": "jpeg",
            "data": encoded,
            "size": len(buffer.getvalue())
        }
    except ImportError:
        # Fallback to scrot if PIL not available
        try:
            import subprocess
            subprocess.run(["scrot", "/tmp/rs_screenshot.jpg"], check=True)
            with open("/tmp/rs_screenshot.jpg", "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return {"success": True, "format": "jpeg", "data": encoded, "size": len(encoded)}
        except Exception as e:
            return {"success": False, "message": f"PIL not installed, and scrot failed: {e}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def capture_windows_screenshot(quality=85):
    """Capture screenshot on Windows"""
    try:
        from PIL import ImageGrab, Image
        import io
        
        img = ImageGrab.grab()
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode()
        
        return {
            "success": True,
            "format": "jpeg",
            "data": encoded,
            "size": len(buffer.getvalue())
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def capture_mac_screenshot(quality=85):
    """Capture screenshot on macOS"""
    try:
        from PIL import ImageGrab, Image
        import io
        
        img = ImageGrab.grab()
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode()
        
        return {
            "success": True,
            "format": "jpeg",
            "data": encoded,
            "size": len(buffer.getvalue())
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def start_screenshot_daemon(interval=30, output_dir="/tmp/rs_screenshots"):
    """Start background screenshot capture"""
    import threading
    import time
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    def daemon():
        i = 0
        while True:
            result = capture_screenshot()
            if result["success"]:
                filepath = f"{output_dir}/screenshot_{i:04d}.jpg"
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(result["data"]))
                i += 1
            time.sleep(interval)
    
    thread = threading.Thread(target=daemon, daemon=True)
    thread.start()
    return {"success": True, "message": f"Screenshot daemon started, saving to {output_dir}"}
