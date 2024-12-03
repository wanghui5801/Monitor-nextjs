@echo off
setlocal enabledelayedexpansion

:: Color definitions for Windows
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Function to print colored messages
call :print_message "Starting installation..." "GREEN"

:: Request administrator privileges
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    call :print_message "Please run as administrator" "RED"
    pause
    exit /b 1
)

:: Get server IP from environment variable or prompt
if "%SERVER_IP%"=="" (
    set /p SERVER_IP=Enter server IP address: 
    if "!SERVER_IP!"=="" (
        call :print_message "Server IP address is required" "RED"
        pause
        exit /b 1
    )
)

:: Get node name
set NODE_NAME=%1
if "%NODE_NAME%"=="" (
    set /p NODE_NAME=Enter node name (press Enter to use hostname): 
    if "!NODE_NAME!"=="" set NODE_NAME=%COMPUTERNAME%
)

:: Check Python version
for /f "tokens=2 delims=." %%I in ('python -c "import sys; print(sys.version.split()[0])"') do (
    if %%I LSS 8 (
        call :print_message "Python 3.8+ is required" "RED"
        pause
        exit /b 1
    )
)

:: Check Git installation
git --version >nul 2>&1
if %errorLevel% neq 0 (
    call :print_message "Git not found. Please install Git first." "RED"
    start https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Backup existing installation
if exist "C:\server-monitor-client" (
    set "backup_dir=C:\server-monitor-client.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%"
    call :print_message "Backing up existing installation to !backup_dir!" "YELLOW"
    move "C:\server-monitor-client" "!backup_dir!"
)

:: Create installation directory
mkdir C:\server-monitor-client
cd /d C:\server-monitor-client

:: Clone project
call :print_message "Cloning repository..." "GREEN"
git clone https://github.com/wanghui5801/Monitor-nextjs.git .
if %errorLevel% neq 0 (
    call :print_message "Failed to clone repository" "RED"
    pause
    exit /b 1
)

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate
if %errorLevel% neq 0 (
    call :print_message "Failed to create virtual environment" "RED"
    pause
    exit /b 1
)

:: Install dependencies
cd client
pip install -r requirements.txt psutil requests wmi
if %errorLevel% neq 0 (
    call :print_message "Failed to install Python dependencies" "RED"
    pause
    exit /b 1
)

:: Create config file
echo API_URL = "http://%SERVER_IP%:5000/api/servers/update" > config.py
echo NODE_NAME = "%NODE_NAME%" >> config.py

:: Download and install NSSM
if not exist "C:\Windows\System32\nssm.exe" (
    call :print_message "Installing NSSM..." "GREEN"
    curl -L -o nssm.zip https://nssm.cc/release/nssm-2.24.zip
    powershell -command "Expand-Archive -Path nssm.zip -DestinationPath C:\nssm-temp"
    move /y "C:\nssm-temp\nssm-2.24\win64\nssm.exe" "C:\Windows\System32\"
    rd /s /q "C:\nssm-temp"
    del nssm.zip
)

:: Create and configure Windows service
call :print_message "Creating Windows service..." "GREEN"
nssm install ServerMonitorClient "%~dp0venv\Scripts\python.exe" "%~dp0client\monitor.py --name %NODE_NAME%"
nssm set ServerMonitorClient AppDirectory "%~dp0client"
nssm set ServerMonitorClient DisplayName "Server Monitor Client"
nssm set ServerMonitorClient Description "Server monitoring client service"
nssm set ServerMonitorClient AppStdout "%~dp0client\service.log"
nssm set ServerMonitorClient AppStderr "%~dp0client\error.log"
nssm set ServerMonitorClient Start SERVICE_AUTO_START

:: Start service
call :print_message "Starting service..." "GREEN"
net start ServerMonitorClient
if %errorLevel% neq 0 (
    call :print_message "Failed to start service. Check logs in client\error.log" "RED"
    pause
    exit /b 1
)

call :print_message "Installation completed successfully!" "GREEN"
call :print_message "Service is running with node name: %NODE_NAME%" "GREEN"
pause
exit /b 0

:print_message
echo %~2%~1%NC%
exit /b 0