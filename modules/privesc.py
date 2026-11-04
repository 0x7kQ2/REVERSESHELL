# Privilege Escalation Module
import platform
import os
import subprocess
import json
from pathlib import Path
import glob

class PrivilegeEscalation:
    def __init__(self):
        self.system = platform.system()
        self.findings = []
        
    def scan_all(self):
        """Run all privilege escalation checks"""
        results = {
            "system": self.system,
            "current_user": os.getlogin() if hasattr(os, 'getlogin') else "unknown",
            "is_root": os.geteuid() == 0 if hasattr(os, 'geteuid') else "unknown",
            "checks": {}
        }
        
        if self.system == "Linux":
            results["checks"]["sudo"] = self.check_sudo()
            results["checks"]["sudoers"] = self.check_sudoers()
            results["checks"]["suid_binaries"] = self.find_suid_binaries()
            results["checks"]["capabilities"] = self.check_capabilities()
            results["checks"]["writable_files"] = self.find_writable_files()
            results["checks"]["cron"] = self.check_cron()
            results["checks"]["kernel"] = self.check_kernel()
            results["checks"]["services"] = self.check_services()
        elif self.system == "Windows":
            results["checks"]["admin"] = self.check_windows_admin()
            results["checks"]["services"] = self.check_windows_services()
            results["checks"]["registry"] = self.check_windows_registry()
            results["checks"]["scheduled_tasks"] = self.check_scheduled_tasks()
        elif self.system == "Darwin":
            results["checks"]["sudo"] = self.check_sudo()
            results["checks"]["suid"] = self.find_suid_binaries()
            results["checks"]["launchd"] = self.check_launchd()
        
        return results
    
    def check_sudo(self):
        """Check sudo configuration"""
        try:
            checks = []
            
            # Check if sudo is available
            result = subprocess.run(['which', 'sudo'], capture_output=True)
            if result.returncode == 0:
                checks.append({"sudo_installed": True})
                
                # Check if we can run sudo without password
                result = subprocess.run(
                    ['sudo', '-n', 'whoami'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    checks.append({"passwordless_sudo": True, "output": result.stdout})
                
                # Check sudoers file
                result = subprocess.run(
                    ['sudo', '-n', 'visudo', '-c'],
                    capture_output=True, text=True
                )
                checks.append({"sudoers_valid": "valid" in result.stdout.lower()})
            
            return {"success": True, "checks": checks}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_sudoers(self):
        """Check sudoers for misconfigurations"""
        try:
            findings = []
            
            # Try to read sudoers
            sudoers_paths = [
                '/etc/sudoers',
                '/etc/sudoers.d/*',
            ]
            
            for path in sudoers_paths:
                for filepath in glob.glob(path):
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            
                            # Check for NOPASSWD
                            if 'NOPASSWD' in content:
                                findings.append({
                                    "file": filepath,
                                    "issue": "NOPASSWD found",
                                    "severity": "HIGH"
                                })
                            
                            # Check for ALL=(ALL)
                            if 'ALL=(ALL)' in content:
                                findings.append({
                                    "file": filepath,
                                    "issue": "Unrestricted sudo access",
                                    "severity": "HIGH"
                                })
                    except:
                        pass
            
            return {"success": True, "findings": findings}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_suid_binaries(self):
        """Find SUID binaries"""
        try:
            suid_files = []
            
            # Common dangerous SUID binaries
            dangerous = [
                'find', 'nmap', 'vim', 'nano', 'less', 'more',
                'python', 'perl', 'ruby', 'awk', 'sed', 'bash',
                'sh', 'zsh', 'ksh', 'tar', 'cp', 'mv', 'rsync'
            ]
            
            result = subprocess.run(
                ['find', '/', '-perm', '-4000', '-type', 'f', '2>/dev/null'],
                capture_output=True, text=True
            )
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    binary = Path(line).name
                    if binary in dangerous:
                        suid_files.append({
                            "path": line,
                            "binary": binary,
                            "exploitable": True,
                            "severity": "HIGH"
                        })
                    else:
                        suid_files.append({
                            "path": line,
                            "binary": binary,
                            "exploitable": False
                        })
            
            return {"success": True, "suid_files": suid_files[:50]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_capabilities(self):
        """Check Linux capabilities"""
        try:
            capabilities = []
            
            result = subprocess.run(
                ['getcap', '-r', '/'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        capabilities.append(line)
            
            return {"success": True, "capabilities": capabilities}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_writable_files(self):
        """Find world-writable files in sensitive locations"""
        try:
            writable = []
            
            sensitive_paths = [
                '/etc/passwd',
                '/etc/shadow',
                '/etc/sudoers',
                '/usr/local/bin',
                '/usr/bin',
                '/bin',
                '/sbin',
            ]
            
            for path in sensitive_paths:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        mode = oct(os.stat(path).st_mode)[-3:]
                        if '6' in mode or '7' in mode:
                            writable.append({
                                "path": path,
                                "mode": mode,
                                "severity": "MEDIUM"
                            })
                    else:
                        # Check directory contents
                        try:
                            for item in os.listdir(path):
                                item_path = os.path.join(path, item)
                                if os.path.isfile(item_path):
                                    mode = oct(os.stat(item_path).st_mode)[-3:]
                                    if '6' in mode or '7' in mode:
                                        writable.append({
                                            "path": item_path,
                                            "mode": mode,
                                            "severity": "LOW"
                                        })
                        except:
                            pass
            
            return {"success": True, "writable_files": writable[:50]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_cron(self):
        """Check cron jobs for escalation opportunities"""
        try:
            cron_jobs = []
            
            # Check system cron
            for cron_dir in ['/etc/cron.d', '/etc/cron.daily', '/etc/cron.hourly']:
                if os.path.exists(cron_dir):
                    for item in os.listdir(cron_dir):
                        item_path = os.path.join(cron_dir, item)
                        if os.path.isfile(item_path):
                            try:
                                mode = oct(os.stat(item_path).st_mode)[-3:]
                                if '6' in mode or '7' in mode:
                                    cron_jobs.append({
                                        "path": item_path,
                                        "mode": mode,
                                        "exploitable": True
                                    })
                            except:
                                pass
            
            return {"success": True, "cron_jobs": cron_jobs}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_kernel(self):
        """Check kernel version for known exploits"""
        try:
            result = subprocess.run(
                ['uname', '-r'],
                capture_output=True, text=True
            )
            
            kernel = result.stdout.strip()
            
            # Known vulnerable kernels
            vulnerable = {
                "4.4": "Dirty Cow (CVE-2016-5195)",
                "3.x": "Various old exploits",
            }
            
            findings = []
            for version, exploit in vulnerable.items():
                if version in kernel:
                    findings.append({
                        "kernel": kernel,
                        "exploit": exploit,
                        "severity": "HIGH"
                    })
            
            return {
                "success": True,
                "kernel_version": kernel,
                "findings": findings
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_services(self):
        """Check services for escalation opportunities"""
        try:
            findings = []
            
            # Check for Docker
            if os.path.exists('/var/run/docker.sock'):
                findings.append({
                    "service": "Docker",
                    "issue": "Docker socket accessible",
                    "exploit": "docker exec -it --privileged -v /:/host <container> nsenter -t 1 -m -u -n -i bash",
                    "severity": "CRITICAL"
                })
            
            # Check for Kubernetes
            if os.path.exists('/var/run/secrets/kubernetes.io'):
                findings.append({
                    "service": "Kubernetes",
                    "issue": "K8s service account tokens present",
                    "severity": "HIGH"
                })
            
            return {"success": True, "findings": findings}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_windows_admin(self):
        """Check Windows admin privileges"""
        try:
            import subprocess
            
            checks = []
            
            # Check if running as admin
            result = subprocess.run(
                ['whoami', '/groups'],
                capture_output=True, text=True
            )
            
            if 'Administrators' in result.stdout:
                checks.append({"is_admin": True})
            else:
                checks.append({"is_admin": False})
            
            # Check for UAC bypass opportunities
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', '/v', 'EnableLUA'],
                capture_output=True, text=True
            )
            
            if '0' in result.stdout:
                checks.append({"uac_disabled": True})
            
            return {"success": True, "checks": checks}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_windows_services(self):
        """Check Windows services for weak permissions"""
        try:
            import subprocess
            
            findings = []
            
            # List services
            result = subprocess.run(
                ['sc', 'query'],
                capture_output=True, text=True
            )
            
            # Check for services with weak permissions
            services = []
            for line in result.stdout.split('\n'):
                if 'SERVICE_NAME' in line:
                    service = line.split(':')[-1].strip()
                    services.append(service)
            
            return {"success": True, "services": services[:20]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_windows_registry(self):
        """Check Windows Registry for escalation opportunities"""
        try:
            import subprocess
            
            findings = []
            
            # Check AutoRun keys
            keys = [
                'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce',
                'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
            ]
            
            for key in keys:
                try:
                    result = subprocess.run(
                        ['reg', 'query', key],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        findings.append({
                            "key": key,
                            "data": result.stdout[:1000]
                        })
                except:
                    pass
            
            return {"success": True, "findings": findings}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_scheduled_tasks(self):
        """Check scheduled tasks for weak permissions"""
        try:
            import subprocess
            
            tasks = []
            
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'LIST'],
                capture_output=True, text=True
            )
            
            if result.stdout:
                tasks.append({"tasks": result.stdout[:3000]})
            
            return {"success": True, "tasks": tasks}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_launchd(self):
        """Check macOS launchd for escalation"""
        try:
            findings = []
            
            # Check LaunchAgents and LaunchDaemons
            paths = [
                '/Library/LaunchAgents',
                '/Library/LaunchDaemons',
                '/System/Library/LaunchDaemons',
            ]
            
            for path in paths:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isfile(item_path):
                            mode = oct(os.stat(item_path).st_mode)[-3:]
                            if '6' in mode or '7' in mode:
                                findings.append({
                                    "path": item_path,
                                    "mode": mode,
                                    "severity": "MEDIUM"
                                })
            
            return {"success": True, "findings": findings}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def exploit_sudo(self, command):
        """Execute command with sudo"""
        try:
            result = subprocess.run(
                ['sudo', '-n', command],
                capture_output=True, text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def scan_privesc():
    """Quick privilege escalation scan"""
    pe = PrivilegeEscalation()
    return pe.scan_all()
