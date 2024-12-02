import psutil
import requests
import time
import platform
import os
import socket
import hashlib
import subprocess
import argparse

# 全局变量定义
CACHED_LOCATION = None
NODE_NAME = socket.gethostname()  # 默认使用主机名
SERVER_ID = None  # 将在 get_machine_id() 后初始化
API_URL = "http://13.70.189.213:5000/api/servers/update"

def parse_arguments():
    parser = argparse.ArgumentParser(description='Server Monitor Client')
    parser.add_argument('--name', type=str, help='Custom node name')
    return parser.parse_args()

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
    try:
        # 获取初始值
        net1 = psutil.net_io_counters()
        time.sleep(1)  # 等待1秒
        # 获取终值
        net2 = psutil.net_io_counters()
        # 计算每秒速率
        bytes_sent = net2.bytes_sent - net1.bytes_sent
        bytes_recv = net2.bytes_recv - net1.bytes_recv
        return bytes_recv, bytes_sent
    except Exception as e:
        print(f"Error getting network speed: {e}")
        return 0, 0

def get_detailed_os_info():
    if platform.system() == 'Windows':
        try:
            import wmi
            w = wmi.WMI()
            os_info = w.Win32_OperatingSystem()[0]
            return f"Windows {os_info.Version}"
        except:
            return "Windows"
    else:
        try:
            # 尝试读取 os-release 文件获取详细信息
            with open('/etc/os-release') as f:
                lines = f.readlines()
                os_info = dict(line.strip().split('=', 1) for line in lines if '=' in line)
                
                # 获取发行版名称
                if 'ID' in os_info:
                    distro_id = os_info['ID'].strip('"')
                    if distro_id == 'ubuntu':
                        return 'Ubuntu'
                    elif distro_id == 'debian':
                        return 'Debian'
                    elif distro_id == 'centos':
                        return 'CentOS'
                    elif distro_id == 'fedora':
                        return 'Fedora'
                    elif distro_id == 'rhel':
                        return 'RHEL'
            
            # 如果上面的方法失败，尝试使用 platform 模块
            dist = platform.dist()
            if dist[0]:
                return dist[0].capitalize()
                
        except:
            # 如果都失败了，使用 platform.system()
            pass
            
    return platform.system()

def get_cpu_info():
    try:
        if platform.system() == "Windows":
            import wmi
            w = wmi.WMI()
            cpu = w.Win32_Processor()[0]
            return f"{cpu.Name} ({psutil.cpu_count()} threads)"
        else:
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if line.startswith('model name'):
                        model = line.split(':')[1].strip()
                        return f"{model} ({psutil.cpu_count()} threads)"
            # 如果无法读取 model name，返回基本信息
            return f"CPU ({psutil.cpu_count()} threads)"
    except Exception as e:
        print(f"Error getting CPU info: {e}")
        return f"CPU ({psutil.cpu_count()} threads)"

def get_all_disks_usage():
    try:
        total_size = 0
        total_used = 0
        # 获取所有磁盘分区
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                # 跟踪所有可以访问的分区
                usage = psutil.disk_usage(partition.mountpoint)
                total_size += usage.total
                total_used += usage.used
            except (PermissionError, OSError):
                # 跳过无法访问的分区
                continue
                
        # 如果有有效的磁盘数据
        if total_size > 0:
            # 计算总体使用百分比
            usage_percent = (total_used / total_size) * 100
            # 转换为GB
            total_size_gb = total_size / (1024 * 1024 * 1024)
            return usage_percent, total_size_gb
            
        return 0, 0
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return 0, 0

def get_server_info():
    network_in, network_out = get_network_speed()
    memory = psutil.virtual_memory()
    disk_percent, total_disk = get_all_disks_usage()
    
    return {
        'id': SERVER_ID,
        'name': NODE_NAME,  # 使用全局的 NODE_NAME
        'type': get_server_type(),
        'location': get_location_from_ip(),
        'uptime': int(time.time() - psutil.boot_time()),
        'network_in': network_in,
        'network_out': network_out,
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': disk_percent,
        'os_type': get_detailed_os_info(),
        'cpu_info': get_cpu_info(),
        'total_memory': psutil.virtual_memory().total / (1024 * 1024 * 1024),
        'total_disk': total_disk
    }

def get_server_type():
    """Determine if server is VPS or Dedicated through multiple checks"""
    if platform.system() == "Windows":
        try:
            import wmi
            w = wmi.WMI()
            # 检查系统型号
            for item in w.Win32_ComputerSystem():
                if any(virt in item.Model.lower() for virt in [
                    'virtual', 'vmware', 'kvm', 'xen', 'hyperv'
                ]):
                    return "VPS"
                    
            # 检查制造商
            for item in w.Win32_ComputerSystem():
                if any(virt in item.Manufacturer.lower() for virt in [
                    'vmware', 'microsoft corporation', 'xen', 'qemu', 'innotek'
                ]):
                    return "VPS"
        except:
            pass
    else:
        # Linux detection methods
        try:
            # Method 1: Check systemd-detect-virt
            try:
                result = subprocess.run(['systemd-detect-virt'], 
                                     capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip() != 'none':
                    return "VPS"
            except:
                pass
                
            # Method 2: Check product name
            with open('/sys/class/dmi/id/product_name') as f:
                product_name = f.read().strip().lower()
                virt_products = [
                    'kvm', 'vmware', 'virtualbox', 'xen', 'openstack', 'qemu',
                    'amazon ec2', 'google compute engine', 
                    'microsoft corporation virtual machine', 'alibaba cloud ecs',
                    'virtual machine', 'bochs', 'standard pc', 
                    'standard personal computer', 'pc-q35', 'q35', 'pc-i440fx',
                    'hetzner vserver', 'vultr', 'linode', 'droplet', 'scaleway',
                    'ovhcloud', 'proxmox', 'parallels', 'hyper-v', 'oracle vm',
                    'innotek', 'cloud server', 'virtual server', 'vps'
                ]
                if any(virt in product_name for virt in virt_products):
                    return "VPS"
                    
            # Method 3: Check CPU info for virtualization flags
            with open('/proc/cpuinfo') as f:
                cpu_info = f.read().lower()
                if any(flag in cpu_info for flag in ['vmx', 'svm', 'hypervisor']):
                    return "VPS"
                    
            # Method 4: Check dmesg for virtualization hints
            try:
                dmesg = subprocess.run(['dmesg'], capture_output=True, text=True).stdout.lower()
                if any(hint in dmesg for hint in ['kvm', 'vmware', 'xen', 'hyperv']):
                    return "VPS"
            except:
                pass
                
        except Exception as e:
            print(f"Error detecting server type: {e}")

    # 如果所有检测都未发现虚拟化特征，则认为是物理服务器
    return "Dedicated Server"

def get_machine_id():
    """获取机器的唯一标识符"""
    try:
        if platform.system() == "Windows":
            # Windows下使用WMI获取系统UUID
            import wmi
            w = wmi.WMI()
            system_info = w.Win32_ComputerSystemProduct()[0]
            return hashlib.md5(system_info.UUID.encode()).hexdigest()
        else:
            # Linux系统保持原有逻辑
            hostname = socket.gethostname()
            mac = subprocess.check_output("cat /sys/class/net/$(ls /sys/class/net | head -n 1)/address", 
                                       shell=True).decode().strip()
            machine_id = f"{hostname}-{mac}"
            return hashlib.md5(machine_id.encode()).hexdigest()
    except Exception as e:
        print(f"Error getting machine ID: {e}")
        # 使用主机名作为后备方案
        return hashlib.md5(socket.gethostname().encode()).hexdigest()

def main():
    global NODE_NAME, SERVER_ID
    
    # 解析命令行参数
    args = parse_arguments()
    if args.name:
        NODE_NAME = args.name
    
    # 初始化 SERVER_ID
    SERVER_ID = get_machine_id()
    
    print(f"Starting monitoring for server: {SERVER_ID}")
    print(f"Node name: {NODE_NAME}")
    print(f"Sending data to: {API_URL}")
    
    while True:
        try:
            system_info = get_server_info()
            response = requests.post(API_URL, json=system_info)
            
            if response.status_code == 200:
                print(f"数据上传成功")
            else:
                print(f"数据上传失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
            print(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(2)  # 每2秒更新一次
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # 发生错误时等待5秒后重试

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控程序已停止")
    except Exception as e:
        print(f"程序异常退出: {e}")
