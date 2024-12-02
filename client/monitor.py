import psutil
import requests
import time
import uuid
import platform
import os
import socket
import requests
import hashlib
import subprocess

SERVER_ID = str(uuid.uuid4())  # 生成唯一ID
API_URL = "http://13.70.189.213:5000/api/servers/update"

# 全局变量保存位置信息
CACHED_LOCATION = None

def get_location_from_ip():
    global CACHED_LOCATION
    if CACHED_LOCATION:
        return CACHED_LOCATION
        
    try:
        # 使用更可靠的 ip-api.com 服务
        response = requests.get('http://ip-api.com/json/', timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            # 获取两位字母的国家代码
            country_code = data.get('countryCode', 'UN')
            CACHED_LOCATION = country_code
            return country_code
            
        # 如果主要 API 失败，尝试备用 API
        ip = requests.get('https://api.ipify.org', timeout=5).text
        response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5).json()
        country_code = response.get('country_code', 'UN')
        CACHED_LOCATION = country_code
        return country_code
        
    except Exception as e:
        print(f"Error getting location: {e}")
        CACHED_LOCATION = 'UN'  # UN 作为默认值，表示未知
        return CACHED_LOCATION

def get_network_speed():
    # 获取初始值
    net1 = psutil.net_io_counters()
    time.sleep(1)  # 等待1秒
    # 获取终值
    net2 = psutil.net_io_counters()
    # 计算每秒速率
    bytes_sent = net2.bytes_sent - net1.bytes_sent
    bytes_recv = net2.bytes_recv - net1.bytes_recv
    return bytes_recv, bytes_sent

def get_detailed_os_info():
    if platform.system() == 'Linux':
        try:
            with open('/etc/os-release') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
    return platform.system()

def get_server_info():
    network_in, network_out = get_network_speed()
    return {
        'id': SERVER_ID,
        'name': socket.gethostname(),
        'type': 'VPS',
        'location': get_location_from_ip(),
        'uptime': int(time.time() - psutil.boot_time()),
        'network_in': network_in,
        'network_out': network_out,
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'os_type': get_detailed_os_info()
    }

def get_server_type():
    """Through system characteristics to determine the server type"""
    if platform.system() == "Windows":
        try:
            import wmi
            w = wmi.WMI()
            for item in w.Win32_ComputerSystem():
                if item.Model.lower().find('virtual') != -1:
                    return "VPS"
        except:
            pass
    else:
        # Linux detection - Check product name
        try:
            with open('/sys/class/dmi/id/product_name') as f:
                product_name = f.read().strip().lower()
                # Common virtualization products
                virt_products = [
                    'kvm', 'vmware', 'virtualbox', 'xen', 'openstack', 'qemu',
                    'amazon ec2', 'google compute engine', 
                    'microsoft corporation virtual machine', 'alibaba cloud ecs',
                    'virtual machine', 'bochs', 'standard pc', 
                    'standard personal computer', 'pc-q35', 'q35', 'pc-i440fx',
                    'hetzner vserver', 'vultr', 'linode', 'droplet', 'scaleway',
                    'ovhcloud', 'proxmox', 'parallels', 'hyper-v', 'oracle vm',
                    'innotek', 'cloud server', 'virtual server', 'vps',
                    '(q35 + ich9', 'ich9', 'standard-pc'
                ]
                
                if any(virt in product_name for virt in virt_products):
                    return "VPS"
                
                return "Dedicated Server"
        except:
            try:
                import subprocess
                result = subprocess.run(['systemd-detect-virt'], 
                                     capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip() != 'none':
                    return "VPS"
            except:
                pass
    
    return "Dedicated Server"

def get_machine_id():
    """获取机器的唯一标识符"""
    # 获取主机名
    hostname = socket.gethostname()
    
    try:
        # 获取第一个网卡的MAC地址
        if platform.system() == "Linux":
            mac = subprocess.check_output("cat /sys/class/net/$(ls /sys/class/net | head -n 1)/address", shell=True).decode().strip()
        elif platform.system() == "Windows":
            mac = subprocess.check_output("getmac /NH").decode().split()[0].strip()
        else:
            mac = "unknown"
    except:
        mac = "unknown"
    
    # 组合主机名和MAC地址，并生成哈希作为机器ID
    machine_id = f"{hostname}-{mac}"
    return hashlib.md5(machine_id.encode()).hexdigest()

# 使用机器ID替代随机UUID
SERVER_ID = get_machine_id()

def main():
    print(f"Starting monitoring for server: {SERVER_ID}")
    print(f"Sending data to: {API_URL}")
    
    while True:
        try:
            system_info = get_server_info()
            response = requests.post(API_URL, json=system_info)
            
            if response.status_code == 200:
                print(f"数据上传成功: {response.status_code}")
            else:
                print(f"数据上传失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
            print(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except requests.RequestException as e:
            print(f"网络错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控程序已停止")
    except Exception as e:
        print(f"程序异常退出: {e}")
