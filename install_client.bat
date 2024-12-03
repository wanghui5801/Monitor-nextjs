@echo off
setlocal enabledelayedexpansion

:: 请求管理员权限
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as administrator
    pause
    exit
)

:: 获取节点名称
set NODE_NAME=%1
if "%NODE_NAME%"=="" (
    set /p NODE_NAME=Enter node name (press Enter to use hostname): 
    if "!NODE_NAME!"=="" set NODE_NAME=%COMPUTERNAME%
)

:: 创建安装目录
mkdir C:\server-monitor-client
cd C:\server-monitor-client

:: 下载并安装Python (如果未安装)
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Python...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

:: 下载并安装NSSM
if not exist "C:\nssm\nssm.exe" (
    echo Installing NSSM...
    curl -L -o nssm.zip https://nssm.cc/release/nssm-2.24.zip
    powershell -command "Expand-Archive -Path nssm.zip -DestinationPath C:\"
    move C:\nssm-2.24\win64\nssm.exe C:\Windows\System32\
    rd /s /q C:\nssm-2.24
    del nssm.zip
)

:: 克隆项目
git clone https://github.com/wanghui5801/Monitor-nextjs.git .

:: 创建虚拟环境
python -m venv venv
call venv\Scripts\activate

:: 安装依赖
cd client
pip install psutil requests wmi

:: 创建Windows服务
echo Creating Windows service...
nssm install ServerMonitorClient "C:\server-monitor-client\venv\Scripts\python.exe" "C:\server-monitor-client\client\monitor.py --name !NODE_NAME!"
nssm set ServerMonitorClient AppDirectory "C:\server-monitor-client\client"
nssm set ServerMonitorClient DisplayName "Server Monitor Client"
nssm set ServerMonitorClient Description "Server monitoring client service"
nssm set ServerMonitorClient Start SERVICE_AUTO_START

:: 启动服务
net start ServerMonitorClient

echo Installation completed with node name: !NODE_NAME!
pause