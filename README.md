# Server Monitor

A distributed server monitoring system that provides real-time metrics and status information for multiple servers.

## Features

- Real-time monitoring of system metrics:
  - CPU usage and model information
  - Memory usage
  - Disk usage and capacity
  - Server location auto-detection
- Multi-server management
- Automatic server status detection
- Cross-platform support (Windows/Linux)
- Dark mode support
- Easy installation with automated scripts

## Quick Start

### Server Installation (Linux Only)

Supported distributions: Ubuntu, Debian, CentOS, RHEL, Fedora

```bash
wget -O install.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_server.sh
chmod +x install.sh
sudo ./install.sh
```

For Windows (Run PowerShell as Administrator):

```powershell
powershell -Command "& { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.bat' -OutFile 'install_client.bat'; Start-Process -FilePath 'install_client.bat' -ArgumentList 'YOUR_SERVER_NAME' -Verb RunAs }"
```

#### Method 2: Manual Installation

Supported distributions: Ubuntu, Debian, CentOS, RHEL, Fedora

## System Requirements

### Server
- Operating System: Ubuntu/Debian/CentOS/RHEL/Fedora
- Python 3.8+
- Node.js 18+
- Nginx
- 1GB RAM minimum
- 10GB free disk space

### Client
- Operating System: Windows/Linux
- Python 3.8+
- 100MB free disk space
- For Windows: Administrator privileges
- For Linux: Root privileges

## Development Setup

1. Clone the repository

```bash
git clone https://github.com/wanghui5801/Monitor-nextjs.git
cd Monitor-nextjs
```

2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Client setup

```bash
cd client
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python monitor.py --name "TEST_SERVER"
```

## Configuration

### Server
- Backend API port: 5000
- Frontend port: 3000 (development) / 80 (production)
- Database: SQLite3 (located at /opt/server-monitor/backend/monitor.db)

### Client
- Update interval: 2 seconds
- Auto-restart on failure: Yes
- Default API endpoint: http://YOUR_SERVER_IP:5000/api/servers/update

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

After installation, access:
- Dashboard: `http://YOUR_SERVER_IP`
- API: `http://YOUR_SERVER_IP/api`

### Client Installation

#### Method 1: One-Click Installation (Recommended)

For Linux:

```bash
wget -O install.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.sh && chmod +x install.sh && sudo ./install.sh "YOUR_SERVER_NAME"
```

For Windows (Run PowerShell as Administrator):

```powershell
powershell -Command "& { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.bat' -OutFile 'install_client.bat'; Start-Process -FilePath 'install_client.bat' -ArgumentList 'YOUR_SERVER_NAME' -Verb RunAs }"
```

#### Method 2: Manual Installation

[Rest of the installation instructions remain the same...]