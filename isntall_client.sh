#!/bin/bash

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# 获取节点名称
read -p "Enter node name (press Enter to use hostname): " NODE_NAME
if [ -z "$NODE_NAME" ]; then
    NODE_NAME=$(hostname)
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

# 创建项目目录
mkdir -p /opt/server-monitor-client
cd /opt/server-monitor-client

# 克隆项目
git clone https://github.com/wanghui5801/Monitor-nextjs.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd client
pip install psutil requests

# 创建systemd服务
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

# 启动服务
systemctl daemon-reload
systemctl enable server-monitor-client
systemctl start server-monitor-client

echo "Client installation completed with node name: ${NODE_NAME}"