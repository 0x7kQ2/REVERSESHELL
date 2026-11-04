# Webcam Module
import platform
import base64
import io
import threading
from pathlib import Path

class WebcamCapture:
    def __init__(self, resolution=(640, 480), fps=15):
        self.resolution = resolution
        self.fps = fps
        self.running = False
        self.thread = None
        self.captured_frames = []
        
    def capture_frame(self):
        """Capture a single frame from webcam"""
        try:
            import cv2
            
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return {"success": False, "message": "Could not open webcam"}
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {"success": False, "message": "Could not read frame"}
            
            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            encoded = base64.b64encode(buffer).decode()
            
            return {
                "success": True,
                "format": "jpeg",
                "data": encoded,
                "resolution": self.resolution
            }
            
        except ImportError:
            return {"success": False, "message": "OpenCV not installed. Run: pip install opencv-python"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def capture_video(self, duration=5):
        """Capture video for specified duration"""
        try:
            import cv2
            import time
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {"success": False, "message": "Could not open webcam"}
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter('/tmp/rs_capture.mp4', fourcc, self.fps, self.resolution)
            
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < duration:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    frame_count += 1
            
            cap.release()
            out.release()
            
            # Read and encode video
            with open('/tmp/rs_capture.mp4', 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
            
            return {
                "success": True,
                "format": "mp4",
                "data": encoded,
                "duration": duration,
                "frames": frame_count
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def list_cameras(self):
        """List available cameras"""
        try:
            import cv2
            
            cameras = []
            for i in range(10):  # Check first 10 indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cameras.append({
                            "index": i,
                            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        })
                    cap.release()
            
            return {"success": True, "cameras": cameras}
            
        except Exception as e:
            return {"success": False, "message": str(e)}


def capture_webcam(resolution=(640, 480)):
    """Quick capture function"""
    wc = WebcamCapture(resolution=resolution)
    return wc.capture_frame()


def capture_webcam_video(duration=5):
    """Quick video capture function"""
    wc = WebcamCapture()
    return wc.capture_video(duration)


def list_cameras():
    """List available cameras"""
    wc = WebcamCapture()
    return wc.list_cameras()
