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

# Function to check minimum system requirements
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
}

# Function to detect and validate OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    else
        OS="unknown"
    fi

    case $OS in
        "debian"|"ubuntu"|"centos"|"rhel"|"fedora")
            print_message "Detected OS: $OS" "$GREEN"
            ;;
        *)
            print_message "Unsupported operating system" "$RED"
            exit 1
            ;;
    esac
}

# Function to check and install Node.js
install_nodejs() {
    if ! check_command "node"; then
        case $OS in
            "debian"|"ubuntu")
                curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
                apt-get install -y nodejs
                ;;
            "centos"|"rhel"|"fedora")
                curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
                yum install -y nodejs
                ;;
        esac
    fi

    # Verify Node.js version
    node_version=$(node -v | cut -d'v' -f2)
    if [ "$(echo "$node_version 18.0.0" | tr " " "\n" | sort -V | head -n1)" != "18.0.0" ]; then
        print_message "Node.js version 18+ is required" "$RED"
        exit 1
    fi
}

# Function to install required packages
install_packages() {
    print_message "Installing required packages..." "$GREEN"
    case $OS in
        "debian"|"ubuntu")
            apt-get update
            apt-get install -y python3 python3-pip python3-venv git curl nginx
            ;;
        "centos"|"rhel"|"fedora")
            yum -y update
            yum -y install python3 python3-pip git curl nginx
            ;;
    esac
}

# Function to backup existing installation
backup_existing() {
    if [ -d "/opt/server-monitor" ]; then
        backup_dir="/opt/server-monitor.backup.$(date +%Y%m%d_%H%M%S)"
        print_message "Backing up existing installation to $backup_dir" "$YELLOW"
        mv /opt/server-monitor "$backup_dir"
    fi
}

# Main installation process
main() {
    print_message "Starting Server Monitor installation..." "$GREEN"
    
    # Initial checks
    detect_os
    check_system_requirements
    backup_existing
    
    # Install dependencies
    install_packages
    install_nodejs
    
    # Create project directory
    mkdir -p /opt/server-monitor
    cd /opt/server-monitor || exit
    
    # Clone project
    if ! git clone https://github.com/wanghui5801/Monitor-nextjs.git .; then
        print_message "Failed to clone repository" "$RED"
        exit 1
    fi
    
    # Install and build frontend
    cd frontend || exit
    if ! npm install; then
        print_message "Failed to install frontend dependencies" "$RED"
        exit 1
    fi
    if ! npm run build; then
        print_message "Failed to build frontend" "$RED"
        exit 1
    fi
    
    # Configure Nginx
    cat > /etc/nginx/conf.d/monitor.conf << 'EOL'
server {
    listen 80;
    server_name _;

    location / {
        root /opt/server-monitor/frontend/.next;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

    # Configure backend
    cd ../backend || exit
    python3 -m venv venv
    source venv/bin/activate
    if ! pip install -r requirements.txt; then
        print_message "Failed to install Python dependencies" "$RED"
        exit 1
    fi

    # Create environment file
    cat > .env << EOL
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
DATABASE_PATH=/opt/server-monitor/backend/monitor.db
EOL

    # Create systemd service
    cat > /etc/systemd/system/server-monitor.service << EOL
[Unit]
Description=Server Monitor Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/server-monitor/backend
Environment="PATH=/opt/server-monitor/backend/venv/bin"
ExecStart=/opt/server-monitor/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

    # Set correct permissions
    chmod 644 /etc/systemd/system/server-monitor.service
    chmod 644 /etc/nginx/conf.d/monitor.conf

    # Start services
    systemctl daemon-reload
    systemctl enable nginx server-monitor
    systemctl restart nginx server-monitor

    # Final check
    if systemctl is-active --quiet server-monitor && systemctl is-active --quiet nginx; then
        print_message "Installation completed successfully!" "$GREEN"
        print_message "You can now access the dashboard at http://YOUR_SERVER_IP" "$GREEN"
    else
        print_message "Installation completed but services are not running properly" "$RED"
        print_message "Please check the logs with: journalctl -u server-monitor" "$YELLOW"
    fi
}

# Error handling
set -e
trap 'print_message "An error occurred. Installation failed!" "$RED"' ERR

# Run main installation
main