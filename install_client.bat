@echo off
setlocal enabledelayedexpansion

:: Colors
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "NC=[0m"

:: Check parameters
if "%~1"=="" (
    :: Interactive mode
    call :print_message "Enter server IP: " "YELLOW"
    set /p "SERVER_IP="
    call :print_message "Enter node name: " "YELLOW"
    set /p "NODE_NAME="
) else if "%~2"=="" (
    call :print_message "Usage: %~nx0 [node_name server_ip]" "RED"
    pause
    exit /b 1
) else (
    :: Direct parameters mode (from admin panel)
    set "NODE_NAME=%~1"
    set "SERVER_IP=%~2"
)

call :print_message "Starting installation..." "GREEN"
call :print_message "Node name: %NODE_NAME%" "GREEN"
call :print_message "Server IP: %SERVER_IP%" "GREEN"

:: Check Python installation
python --version >nul 2>&1
if %errorLevel% neq 0 (
    call :print_message "Python not found. Please install Python first." "RED"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create installation directory
mkdir C:\server-monitor-client 2>nul
cd /d C:\server-monitor-client

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install dependencies
pip install psutil requests python-socketio

:: Download monitor.py from repository
powershell -Command "& { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/client/monitor.py' -OutFile 'monitor.py' }"

:: Configure API URL in monitor.py
powershell -Command "& { (Get-Content monitor.py) -replace 'API_URL = .*', 'API_URL = ''http://%SERVER_IP%:5000''' | Set-Content monitor.py }"

:: Create logs directory
mkdir logs 2>nul

:: Install NSSM if not present
if not exist "%ProgramFiles%\nssm\nssm.exe" (
    call :print_message "Installing NSSM..." "YELLOW"
    powershell -Command "& { Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip' }"
    powershell -Command "& { Expand-Archive -Path 'nssm.zip' -DestinationPath '.' }"
    xcopy "nssm-2.24\win64\nssm.exe" "%ProgramFiles%\nssm\" /Y
    rd /s /q "nssm-2.24"
    del nssm.zip
)

:: Create Windows service
"%ProgramFiles%\nssm\nssm.exe" install ServerMonitorClient "C:\server-monitor-client\venv\Scripts\python.exe"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppParameters "C:\server-monitor-client\monitor.py --name %NODE_NAME%"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppDirectory "C:\server-monitor-client"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient DisplayName "Server Monitor Client"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient Description "Server monitoring client service"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient Start SERVICE_AUTO_START
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppStdout "C:\server-monitor-client\logs\service.log"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppStderr "C:\server-monitor-client\logs\error.log"

:: Start service
net start ServerMonitorClient

call :print_message "Installation completed successfully!" "GREEN"
exit /b 0

:print_message
echo %~2%~1%NC%
exit /b 0