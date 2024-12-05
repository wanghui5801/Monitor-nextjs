#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check Python version
check_python_version() {
    if ! command -v python3 &> /dev/null; then
        print_message "Python 3 is required but not installed." "$RED"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    if ! command -v pip3 &> /dev/null; then
        print_message "pip3 is required but not installed." "$RED"
        exit 1
    fi
}

# Main installation
main() {
    # Check if parameters are provided
    if [ $# -eq 0 ]; then
        # Interactive mode
        read -p "Enter server IP: " SERVER_IP
        read -p "Enter node name: " NODE_NAME
    elif [ $# -eq 2 ]; then
        # Direct parameters mode (from admin panel)
        NODE_NAME="${1//\"/}"  # Remove any quotes
        SERVER_IP="${2//\"/}"  # Remove any quotes
    else
        print_message "Usage: $0 [node_name server_ip]" "$RED"
        exit 1
    fi
    
    print_message "Starting client installation..." "$GREEN"
    print_message "Node name: $NODE_NAME" "$GREEN"
    print_message "Server IP: $SERVER_IP" "$GREEN"
    
    # Initial checks
    check_python_version
    check_system_requirements
    
    # Create project directory
    mkdir -p /opt/server-monitor-client
    cd /opt/server-monitor-client || exit 1
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install psutil requests python-socketio

    # Download monitor.py from repository
    wget -O monitor.py https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/client/monitor.py

    # Configure API URL in monitor.py
    sed -i "s|API_URL = .*|API_URL = 'http://${SERVER_IP}:5000'|g" monitor.py
    
    # Create systemd service
    cat > /etc/systemd/system/server-monitor-client.service << EOL
[Unit]
Description=Server Monitor Client
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/server-monitor-client
Environment="PATH=/opt/server-monitor-client/venv/bin"
ExecStart=/opt/server-monitor-client/venv/bin/python monitor.py --name "${NODE_NAME}"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

    # Set permissions and start service
    chmod 644 /etc/systemd/system/server-monitor-client.service
    systemctl daemon-reload
    systemctl enable server-monitor-client
    systemctl start server-monitor-client

    print_message "Installation completed successfully!" "$GREEN"
    print_message "Service is running with node name: ${NODE_NAME}" "$GREEN"
}

# Run main installation
main "$@" 