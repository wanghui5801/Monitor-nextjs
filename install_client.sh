#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_message "Please run as root" "$RED"
    exit 1
fi

# Function to check Python version
check_python_version() {
    if ! command -v python3 &> /dev/null; then
        print_message "Python3 not found" "$RED"
        exit 1
    fi
    
    version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [ "$(echo "$version 3.8" | tr " " "\n" | sort -V | head -n1)" != "3.8" ]; then
        print_message "Python 3.8+ is required, found version $version" "$RED"
        exit 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    # Check disk space
    free_space=$(df -m /opt | awk 'NR==2 {print $4}')
    if [ "$free_space" -lt 100 ]; then
        print_message "Warning: Less than 100MB free space available" "$YELLOW"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check git installation
if ! command -v git &> /dev/null; then
    print_message "Git not found. Installing..." "$YELLOW"
    case $OS in
        "debian"|"ubuntu")
            apt-get install -y git
            ;;
        "centos"|"rhel"|"fedora")
            yum install -y git
            ;;
    esac
fi

# Function to backup existing installation
backup_existing() {
    if [ -d "/opt/server-monitor-client" ]; then
        backup_dir="/opt/server-monitor-client.backup.$(date +%Y%m%d_%H%M%S)"
        print_message "Backing up existing installation to $backup_dir" "$YELLOW"
        mv /opt/server-monitor-client "$backup_dir"
    fi
}

# Get node name and server IP
NODE_NAME=$1
if [ -z "$NODE_NAME" ]; then
    read -p "Enter node name (press Enter to use hostname): " NODE_NAME
    if [ -z "$NODE_NAME" ]; then
        NODE_NAME=$(hostname)
    fi
fi

# Get server IP from environment variable or prompt
SERVER_IP=${SERVER_IP:-""}
if [ -z "$SERVER_IP" ]; then
    read -p "Enter server IP address: " SERVER_IP
    if [ -z "$SERVER_IP" ]; then
        print_message "Server IP address is required" "$RED"
        exit 1
    fi
fi

# Main installation
main() {
    print_message "Starting client installation..." "$GREEN"
    
    # Initial checks
    check_python_version
    check_system_requirements
    backup_existing
    
    # Create project directory
    mkdir -p /opt/server-monitor-client
    cd /opt/server-monitor-client || exit 1
    
    # Clone project
    if ! git clone https://github.com/wanghui5801/Monitor-nextjs.git .; then
        print_message "Failed to clone repository" "$RED"
        exit 1
    fi
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    cd client || exit 1
    if ! pip install -r requirements.txt psutil requests; then
        print_message "Failed to install Python dependencies" "$RED"
        exit 1
    fi
    
    # Create config file
    cat > config.py << EOL
API_URL = "http://${SERVER_IP}:5000/api/servers/update"
NODE_NAME = "${NODE_NAME}"
EOL
    
    # Create systemd service
    cat > /etc/systemd/system/server-monitor-client.service << EOL
[Unit]
Description=Server Monitor Client
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/server-monitor-client/client
Environment="PATH=/opt/server-monitor-client/venv/bin"
ExecStart=/opt/server-monitor-client/venv/bin/python monitor.py --name "${NODE_NAME}"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

    # Set permissions
    chmod 644 /etc/systemd/system/server-monitor-client.service
    
    # Start service
    systemctl daemon-reload
    systemctl enable server-monitor-client
    if ! systemctl start server-monitor-client; then
        print_message "Failed to start service" "$RED"
        exit 1
    fi
    
    # Verify service status
    if systemctl is-active --quiet server-monitor-client; then
        print_message "Installation completed successfully!" "$GREEN"
        print_message "Service is running with node name: ${NODE_NAME}" "$GREEN"
    else
        print_message "Service failed to start" "$RED"
        print_message "Check logs with: journalctl -u server-monitor-client" "$YELLOW"
        exit 1
    fi
}

# Error handling
set -e
trap 'print_message "An error occurred. Installation failed!" "$RED"' ERR

# Run main installation
main 