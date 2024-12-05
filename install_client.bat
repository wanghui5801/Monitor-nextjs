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
    echo %YELLOW%Enter server IP: %NC%
    set /p "SERVER_IP="
    echo %YELLOW%Enter node name: %NC%
    set /p "NODE_NAME="
) else if "%~2"=="" (
    echo %RED%Usage: %~nx0 [node_name server_ip]%NC%
    pause
    exit /b 1
) else (
    :: Direct parameters mode (from admin panel)
    set "NODE_NAME=%~1"
    set "SERVER_IP=%~2"
)

echo %GREEN%Starting installation...%NC%
echo %GREEN%Node name: %NODE_NAME%%NC%
echo %GREEN%Server IP: %SERVER_IP%%NC%

:: Check Python installation
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%Python not found. Please install Python first.%NC%
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
pip install psutil requests "python-socketio[client]" wmi

:: Download monitor.py from repository
powershell -Command "& { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/client/monitor.py' -OutFile 'monitor.py' }"

:: Configure API URL in monitor.py
powershell -Command "& { (Get-Content monitor.py) -replace 'API_URL = .*', 'API_URL = ''http://%SERVER_IP%:5000''' | Set-Content monitor.py -Encoding UTF8 }"

:: Create logs directory
mkdir logs 2>nul

:: Install NSSM if not present
if not exist "%ProgramFiles%\nssm\nssm.exe" (
    echo %YELLOW%Installing NSSM...%NC%
    powershell -Command "& { Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip' }"
    powershell -Command "& { Expand-Archive -Path 'nssm.zip' -DestinationPath '.' }"
    xcopy "nssm-2.24\win64\nssm.exe" "%ProgramFiles%\nssm\" /Y /I
    rd /s /q "nssm-2.24"
    del nssm.zip
)

:: Stop existing service if running
net stop ServerMonitorClient 2>nul
"%ProgramFiles%\nssm\nssm.exe" remove ServerMonitorClient confirm 2>nul

:: Create Windows service with UTF-8 encoding
"%ProgramFiles%\nssm\nssm.exe" install ServerMonitorClient "C:\server-monitor-client\venv\Scripts\python.exe"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppParameters "-X utf8 C:\server-monitor-client\monitor.py --name %NODE_NAME%"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppDirectory "C:\server-monitor-client"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient DisplayName "Server Monitor Client"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient Description "Server monitoring client service"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient Start SERVICE_AUTO_START
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppStdout "C:\server-monitor-client\logs\service.log"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppStderr "C:\server-monitor-client\logs\error.log"
"%ProgramFiles%\nssm\nssm.exe" set ServerMonitorClient AppEnvironmentExtra "PYTHONIOENCODING=utf-8"

:: Start service
net start ServerMonitorClient

echo %GREEN%Installation completed successfully!%NC%
echo %GREEN%Check logs at C:\server-monitor-client\logs for any issues%NC%
pause
exit /b 0