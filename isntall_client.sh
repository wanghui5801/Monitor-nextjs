#!/bin/bash

# Check if running as root user
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Configure API URL
read -p "Enter server IP address: " SERVER_IP
sed -i "s|API_URL = .*|API_URL = \"http://${SERVER_IP}:5000/api/servers/update\"|" client/monitor.py

# Get node name
NODE_NAME=$1
if [ -z "$NODE_NAME" ]; then
    read -p "Enter node name (press Enter to use hostname): " NODE_NAME
    if [ -z "$NODE_NAME" ]; then
        NODE_NAME=$(hostname)
    fi
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif [ -f /etc/redhat-release ]; then
    OS="rhel"
else
    OS="unknown"
fi

# Install required packages
case $OS in
    "debian"|"ubuntu")
        apt-get update
        apt-get install -y python3 python3-pip python3-venv git
        ;;
    "centos"|"rhel"|"fedora")
        yum -y update
        yum -y install python3 python3-pip git
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Create project directory
mkdir -p /opt/server-monitor-client
cd /opt/server-monitor-client

# Clone project
git clone https://github.com/wanghui5801/Monitor-nextjs.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd client
pip install psutil requests

# Create systemd service
cat > /etc/systemd/system/server-monitor-client.service << EOL
[Unit]
Description=Server Monitor Client
After=network.target

[Service]
User=root
WorkingDirectory=/opt/server-monitor-client/client
Environment="PATH=/opt/server-monitor-client/venv/bin"
ExecStart=/opt/server-monitor-client/venv/bin/python monitor.py --name "${NODE_NAME}"
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Start service
systemctl daemon-reload
systemctl enable server-monitor-client
systemctl start server-monitor-client

echo "Client installation completed with node name: ${NODE_NAME}"