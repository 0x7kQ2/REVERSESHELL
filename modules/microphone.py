# Microphone Module
import platform
import base64
import threading
import wave
import io

class MicrophoneRecorder:
    def __init__(self, chunk=1024, rate=44100, channels=1, fmt=2):
        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.fmt = fmt  # 2 = 16-bit
        self.running = False
        self.thread = None
        self.frames = []
        
    def record(self, duration=10):
        """Record audio for specified duration"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.frames = []
            self.running = True
            
            import time
            start_time = time.time()
            
            while time.time() - start_time < duration:
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            
            self.running = False
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to WAV
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode()
            
            return {
                "success": True,
                "format": "wav",
                "data": encoded,
                "duration": duration,
                "size": len(buffer.getvalue())
            }
            
        except ImportError:
            return {"success": False, "message": "PyAudio not installed. Run: pip install pyaudio"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def list_devices(self):
        """List available audio devices"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append({
                        "index": i,
                        "name": info['name'],
                        "channels": info['maxInputChannels'],
                        "sample_rate": info['defaultSampleRate']
                    })
            
            p.terminate()
            return {"success": True, "devices": devices}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def start_recording(self):
        """Start continuous recording"""
        if self.running:
            return {"success": False, "message": "Already recording"}
        
        self.frames = []
        self.running = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()
        
        return {"success": True, "message": "Recording started"}
    
    def stop_recording(self):
        """Stop recording and return audio"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        if not self.frames:
            return {"success": False, "message": "No audio recorded"}
        
        # Save to WAV
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode()
        
        return {
            "success": True,
            "format": "wav",
            "data": encoded,
            "size": len(buffer.getvalue())
        }
    
    def _record_loop(self):
        """Background recording loop"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.running:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                except:
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Recording error: {e}")


def record_audio(duration=10):
    """Quick record function"""
    mic = MicrophoneRecorder()
    return mic.record(duration)


def list_audio_devices():
    """List audio devices"""
    mic = MicrophoneRecorder()
    return mic.list_devices()
