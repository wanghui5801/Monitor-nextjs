# Server Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg)](https://github.com/wanghui5801/Monitor-nextjs)

A user-friendly, real-time monitoring system for distributed servers with an intuitive dashboard interface.

## Key Features

✨ Real-time System Metrics:
- CPU usage & model information
- Memory utilization
- Disk space monitoring
- Automatic location detection
- Network traffic monitoring

🌟 Additional Features:
- Multi-server management
- Automatic status detection
- Cross-platform (Windows/Linux)
- Dark/Light mode
- One-click installation

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

## System Requirements

### Server
- OS: Ubuntu/Debian/CentOS/RHEL/Fedora
- Python 3.8+
- Node.js 18+
- 1GB RAM minimum
- 10GB free disk space

### Client
- OS: Windows/Linux
- Python 3.8+
- 100MB free disk space
- Admin/Root privileges

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
- Frontend Port: 3000 (dev) / 80 (prod)
- Database: SQLite3 (/opt/server-monitor/backend/monitor.db)

### Client
- Update Interval: 2 seconds
- Auto-restart: Enabled
- API Endpoint: http://YOUR_SERVER_IP:5000

## Support

For issues or feature requests, please open an issue on GitHub.

## License

MIT License - see LICENSE file for details