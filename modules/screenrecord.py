# Screen Recording Module
import platform
import subprocess
import threading
import time
import base64
from pathlib import Path

class ScreenRecorder:
    def __init__(self, fps=15, quality=85):
        self.fps = fps
        self.quality = quality
        self.running = False
        self.thread = None
        self.frames = []
        self.output_file = None
        
    def capture_frame(self):
        """Capture a single frame"""
        try:
            if platform.system() == "Linux":
                return self.capture_linux_frame()
            elif platform.system() == "Windows":
                return self.capture_windows_frame()
            elif platform.system() == "Darwin":
                return self.capture_mac_frame()
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def capture_linux_frame(self):
        """Capture frame on Linux"""
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab()
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=self.quality)
            buffer.seek(0)
            
            encoded = base64.b64encode(buffer.read()).decode()
            
            return {
                "success": True,
                "format": "jpeg",
                "data": encoded,
                "size": len(buffer.getvalue())
            }
        except ImportError:
            # Fallback to ffmpeg
            output = f'/tmp/frame_{int(time.time())}.jpg'
            subprocess.run(
                ['ffmpeg', '-f', 'x11grab', '-i', ':0.0', '-vframes', '1', '-y', output],
                capture_output=True
            )
            
            if Path(output).exists():
                with open(output, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode()
                return {"success": True, "format": "jpeg", "data": encoded}
            
            return {"success": False, "message": "Could not capture frame"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def capture_windows_frame(self):
        """Capture frame on Windows"""
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab()
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=self.quality)
            buffer.seek(0)
            
            encoded = base64.b64encode(buffer.read()).decode()
            
            return {
                "success": True,
                "format": "jpeg",
                "data": encoded,
                "size": len(buffer.getvalue())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def capture_mac_frame(self):
        """Capture frame on macOS"""
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab()
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=self.quality)
            buffer.seek(0)
            
            encoded = base64.b64encode(buffer.read()).decode()
            
            return {
                "success": True,
                "format": "jpeg",
                "data": encoded,
                "size": len(buffer.getvalue())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_video(self, duration=30, output_file='/tmp/screenrecord.mp4'):
        """Record video for specified duration"""
        try:
            self.output_file = output_file
            
            if platform.system() == "Linux":
                return self.record_linux(duration)
            elif platform.system() == "Windows":
                return self.record_windows(duration)
            elif platform.system() == "Darwin":
                return self.record_mac(duration)
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "message": "Platform not supported"}
    
    def record_linux(self, duration: int):
        """Record on Linux using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'x11grab',
                '-i', ':0.0',
                '-vf', f'fps={self.fps}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-t', str(duration),
                self.output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=duration + 10)
            
            if Path(self.output_file).exists():
                with open(self.output_file, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode()
                
                return {
                    "success": True,
                    "format": "mp4",
                    "data": encoded,
                    "duration": duration,
                    "size": len(encoded)
                }
            
            return {"success": False, "message": "Recording failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_windows(self, duration: int):
        """Record on Windows using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'gdigrab',
                '-i', 'desktop',
                '-vf', f'fps={self.fps}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-t', str(duration),
                self.output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=duration + 10)
            
            if Path(self.output_file).exists():
                with open(self.output_file, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode()
                
                return {
                    "success": True,
                    "format": "mp4",
                    "data": encoded,
                    "duration": duration,
                    "size": len(encoded)
                }
            
            return {"success": False, "message": "Recording failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_mac(self, duration: int):
        """Record on macOS using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'avfoundation',
                '-i', ':0',
                '-vf', f'fps={self.fps}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-t', str(duration),
                self.output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=duration + 10)
            
            if Path(self.output_file).exists():
                with open(self.output_file, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode()
                
                return {
                    "success": True,
                    "format": "mp4",
                    "data": encoded,
                    "duration": duration,
                    "size": len(encoded)
                }
            
            return {"success": False, "message": "Recording failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_continuous(self, interval=5, output_dir='/tmp/screenframes'):
        """Start continuous frame capture"""
        self.running = True
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        
        self.thread = threading.Thread(target=self._continuous_loop, args=(interval,), daemon=True)
        self.thread.start()
        
        return {"success": True, "message": f"Continuous capture started, saving to {output_dir}"}
    
    def stop_continuous(self):
        """Stop continuous capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        return {"success": True, "message": "Continuous capture stopped"}
    
    def _continuous_loop(self, interval: int):
        """Continuous capture loop"""
        frame_count = 0
        
        while self.running:
            try:
                result = self.capture_frame()
                if result["success"]:
                    output_path = f'{self.output_dir}/frame_{frame_count:04d}.jpg'
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(result["data"]))
                    frame_count += 1
            except:
                pass
            
            time.sleep(interval)


def capture_screen():
    """Quick screen capture function"""
    sr = ScreenRecorder()
    return sr.capture_frame()


def record_screen(duration=30):
    """Quick screen recording function"""
    sr = ScreenRecorder()
    return sr.record_video(duration)
