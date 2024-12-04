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

# Function to check command existence
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_message "Command $1 not found. Installing..." "$YELLOW"
        return 1
    fi
    return 0
}

# Function to check system requirements
check_system_requirements() {
    # Check RAM
    total_ram=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$total_ram" -lt 1024 ]; then
        print_message "Warning: Less than 1GB RAM available" "$YELLOW"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Check disk space
    free_space=$(df -m /opt | awk 'NR==2 {print $4}')
    if [ "$free_space" -lt 10240 ]; then
        print_message "Warning: Less than 10GB free space available" "$YELLOW"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to install Node.js
install_nodejs() {
    if ! check_command "node"; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi

    # Verify Node.js version
    node_version=$(node -v | cut -d'v' -f2)
    if [ "$(echo "$node_version 18.0.0" | tr " " "\n" | sort -V | head -n1)" != "18.0.0" ]; then
        print_message "Node.js version 18+ is required" "$RED"
        exit 1
    fi
}

# Function to install PM2
install_pm2() {
    if ! check_command "pm2"; then
        npm install -g pm2
    fi
}

# Function to install required packages
install_packages() {
    print_message "Installing required packages..." "$GREEN"
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl
}

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || wget -qO- ifconfig.me)
if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(hostname -I | awk '{print $1}')
fi

# Main installation process
main() {
    print_message "Starting Server Monitor installation..." "$GREEN"
    
    # Initial checks
    check_system_requirements
    
    # Install dependencies
    install_packages
    install_nodejs
    install_pm2
    
    # Create project directory
    mkdir -p /opt/server-monitor
    cd /opt/server-monitor || exit
    
    # Clone project
    if ! git clone https://github.com/wanghui5801/Monitor-nextjs.git .; then
        print_message "Failed to clone repository" "$RED"
        exit 1
    fi
    
    # Frontend setup
    cd frontend || exit
    if ! npm install; then
        print_message "Failed to install frontend dependencies" "$RED"
        exit 1
    fi
    
    # Backend setup
    cd ../backend || exit
    python3 -m venv venv
    source venv/bin/activate
    if ! pip install -r requirements.txt; then
        print_message "Failed to install Python dependencies" "$RED"
        exit 1
    fi

    # Create logs directory
    mkdir -p /opt/server-monitor/logs

    # Start services using PM2
    cd /opt/server-monitor || exit
    if ! pm2 start ecosystem.config.js; then
        print_message "Failed to start services with PM2" "$RED"
        exit 1
    fi

    # Save PM2 process list and set to start on boot
    pm2 save
    pm2 startup

    # Final check
    if pm2 list | grep -q "server-monitor"; then
        print_message "Installation completed successfully!" "$GREEN"
        print_message "You can now access:" "$GREEN"
        print_message "Dashboard: http://${SERVER_IP}:3000" "$GREEN"
        print_message "API: http://${SERVER_IP}:5000" "$GREEN"
    else
        print_message "Installation completed but services are not running properly" "$RED"
        print_message "Please check the logs with: pm2 logs" "$YELLOW"
    fi
}

# Error handling
set -e
trap 'print_message "An error occurred. Installation failed!" "$RED"' ERR

# Run main installation
main