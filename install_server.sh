#!/bin/bash

# Check if running as root user
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
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
        apt-get install -y python3 python3-pip python3-venv git curl nodejs npm nginx
        ;;
    "centos"|"rhel"|"fedora")
        yum -y update
        yum -y install python3 python3-pip git curl
        # Install NodeJS
        curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
        yum install -y nodejs
        # Install Nginx
        yum install -y nginx
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Create project directory
mkdir -p /opt/server-monitor
cd /opt/server-monitor

# Clone project
git clone https://github.com/wanghui5801/Monitor-nextjs.git .

# Install and build frontend
cd frontend
npm install
npm run build

# Configure Nginx
cat > /etc/nginx/conf.d/monitor.conf << EOL
server {
    listen 80;
    server_name _;

    location / {
        root /opt/server-monitor/frontend/.next;
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOL

# Restart Nginx
systemctl enable nginx
systemctl restart nginx

# Install and configure backend
cd ../backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment variable file
cat > .env << EOL
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
DATABASE_PATH=/opt/server-monitor/backend/monitor.db
EOL

# Create backend service
cat > /etc/systemd/system/server-monitor.service << EOL
[Unit]
Description=Server Monitor Backend
After=network.target

[Service]
User=root
WorkingDirectory=/opt/server-monitor/backend
Environment="PATH=/opt/server-monitor/venv/bin"
ExecStart=/opt/server-monitor/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Start backend service
systemctl daemon-reload
systemctl enable server-monitor
systemctl start server-monitor

# Output installation completed information
echo "Server installation completed!"
echo "Frontend: http://YOUR_SERVER_IP"
echo "Backend API: http://YOUR_SERVER_IP/api"
echo "Please update the API_URL in client/monitor.py to match your server IP"