#!/bin/bash

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# 检测Linux发行版
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif [ -f /etc/redhat-release ]; then
    OS="rhel"
else
    OS="unknown"
fi

# 安装必要的包
case $OS in
    "debian"|"ubuntu")
        apt-get update
        apt-get install -y python3 python3-pip python3-venv git curl nodejs npm nginx
        ;;
    "centos"|"rhel"|"fedora")
        yum -y update
        yum -y install python3 python3-pip git curl
        # 安装 NodeJS
        curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
        yum install -y nodejs
        # 安装 Nginx
        yum install -y nginx
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# 创建项目目录
mkdir -p /opt/server-monitor
cd /opt/server-monitor

# 克隆项目
git clone https://github.com/wanghui5801/Monitor-nextjs.git .

# 安装并构建前端
cd frontend
npm install
npm run build

# 配置 Nginx
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

# 重启 Nginx
systemctl enable nginx
systemctl restart nginx

# 安装并配置后端
cd ../backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cat > .env << EOL
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
DATABASE_PATH=/opt/server-monitor/backend/monitor.db
EOL

# 创建后端服务
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

# 启动后端服务
systemctl daemon-reload
systemctl enable server-monitor
systemctl start server-monitor

# 输出安装完成信息
echo "Server installation completed!"
echo "Frontend: http://YOUR_SERVER_IP"
echo "Backend API: http://YOUR_SERVER_IP/api"
echo "Please update the API_URL in client/monitor.py to match your server IP"