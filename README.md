# Server Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg)](https://github.com/wanghui5801/Monitor-nextjs)

![Homepage Screenshot](Figures/homepage.png)

A user-friendly, real-time monitoring system for distributed servers with an intuitive dashboard interface.

## Key Features

✨ Real-time System Metrics:
- CPU usage & model information
- Memory utilization
- Disk space monitoring
- Automatic location detection
- Network traffic monitoring
- IP address protection (IPs are hidden for non-authenticated users)

🌟 Additional Features:
- Multi-server management
- Automatic status detection
- Cross-platform (Windows/Linux)
- Dark/Light mode
- One-click installation
- Secure admin interface

## Security Features

### IP Address Protection
- Public view: IP addresses are masked (displayed as ***.***.***.**)
- Admin view: Full IP addresses visible after authentication
- Secure JWT-based authentication
- Protected API endpoints

## Quick Installation Guide

### 1. Server Setup (Linux Only)

Run this command on your Linux server:

```bash
wget -O install.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_server.sh && chmod +x install.sh && sudo ./install.sh
```

After installation, access:
- Dashboard: `http://YOUR_SERVER_IP`
- API: `http://YOUR_SERVER_IP:5000`

### 2. Client Installation

#### For Linux:

```bash
wget -O install.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.sh && chmod +x install.sh && sudo ./install.sh
```

#### For Windows:
Run PowerShell as Administrator:

```powershell
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.bat' -OutFile 'install_client.bat'; .\install_client.bat
```

## Domain Setup (Optional)

To configure a custom domain with SSL:

1. Ensure you have a domain pointed to your server's IP address
2. Run the domain setup script:

```bash
wget -O setup_domain.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/setup_domain.sh && chmod +x setup_domain.sh && sudo ./setup_domain.sh
```

This script will:
- Install and configure Nginx
- Obtain SSL certificate via Let's Encrypt
- Set up reverse proxy for both frontend and API
- Update application configuration
- Restart all services

After setup, your monitor will be accessible at:
- Dashboard: `https://YOUR_DOMAIN`
- API: `https://YOUR_DOMAIN/api`

### Updating Existing Clients

If you have existing clients, update their API endpoint:

1. Edit the client configuration:

```bash
sudo nano /opt/server-monitor-client/monitor.py
```

2. Update the API_URL:

```python
API_URL = 'https://YOUR_DOMAIN/api'
```

3. Restart the client service:

For Linux:

```bash
sudo systemctl restart server-monitor-client
```

For Windows:

```powershell
Restart-Service ServerMonitorClient
```

## System Requirements

### Server
- OS: Ubuntu/Debian/CentOS/RHEL/Fedora
- **Python 3.8+ (Required)**
- **Required Python packages:**
  - python3-pip
  - python3-venv
- Node.js 18+
- 1GB RAM minimum
- 10GB free disk space

### Client
- OS: Windows/Linux
- **Python 3.8+ (Required)**
- **Required Python packages:**
  - python3-pip
  - python3-venv
- 100MB free disk space
- Admin/Root privileges

### Installing Python Requirements (Linux)

For Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

For CentOS/RHEL:

```bash
sudo dnf install python3 python3-pip python3-venv
```

For Fedora:

```bash
sudo dnf install python3 python3-pip python3-venv
```

## Development Setup

1. Clone and prepare:

```bash
git clone https://github.com/wanghui5801/Monitor-nextjs.git
cd Monitor-nextjs
```

2. Setup Frontend:

```bash
cd frontend
npm install
npm run dev
```

3. Setup Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Configuration

### Server
- API Port: 5000
- Frontend Port: 3000
- Database: SQLite3 (/opt/server-monitor/backend/servers.db)

### Client
- Update Interval: 2 seconds
- Auto-restart: Enabled
- API Endpoint: http://YOUR_SERVER_IP:5000

## Service Management

### Server (PM2)

Monitor server status:

```bash
sudo pm2 status
```

View logs:

```bash
sudo pm2 logs                    # All logs
sudo pm2 logs server-monitor-frontend  # Frontend logs only
sudo pm2 logs server-monitor-backend   # Backend logs only
```

Restart services:

```bash
sudo pm2 restart all            # Restart all
sudo pm2 restart server-monitor-frontend
sudo pm2 restart server-monitor-backend
```

Stop services:

```bash
sudo pm2 stop all              # Stop all
sudo pm2 stop server-monitor-frontend
sudo pm2 stop server-monitor-backend
```

### Client Service

#### Linux (Systemctl)

Check status:

```bash
sudo systemctl status server-monitor-client
```

View logs:

```bash
sudo journalctl -u server-monitor-client -f
```

Manage service:

```bash
sudo systemctl start server-monitor-client
sudo systemctl stop server-monitor-client
sudo systemctl restart server-monitor-client
```

#### Windows (Services)

Using Command Prompt (Admin):

```cmd
net start ServerMonitorClient
net stop ServerMonitorClient
```

Or using PowerShell (Admin):

```powershell
Start-Service ServerMonitorClient
Stop-Service ServerMonitorClient
Restart-Service ServerMonitorClient
Get-Service ServerMonitorClient
```

View logs at:
```
C:\server-monitor-client\logs\service.log
C:\server-monitor-client\logs\error.log
```

## Support

For issues or feature requests, please open an issue on GitHub.

## License

MIT License - see LICENSE file for details