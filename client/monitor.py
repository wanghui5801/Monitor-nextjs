import psutil
import requests
import time
import platform
import os
import socket
import hashlib
import subprocess
import argparse
from socketio import Client

# Set UTF-8 encoding for Windows
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Global variable definitions
CACHED_LOCATION = None
NODE_NAME = socket.gethostname()  # Default to hostname
SERVER_ID = None  # Will be initialized after get_machine_id()

# Get API URL from environment or config file
try:
    from config import API_URL
except ImportError:
    API_URL = os.getenv('API_URL', 'http://localhost:5000/api/servers/update')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Server Monitor Client')
    parser.add_argument('--name', type=str, help='Custom node name', default=socket.gethostname())
    args = parser.parse_args()
    return args.name.strip('"\'')  # Remove any quotes from the name

def get_location_from_ip():
    global CACHED_LOCATION
    if CACHED_LOCATION:
        return CACHED_LOCATION
        
    try:
        # Use more reliable ip-api.com service
        response = requests.get('http://ip-api.com/json/', timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            # Get two-letter country code
            country_code = data.get('countryCode', 'UN')
            CACHED_LOCATION = country_code
            return country_code
            
        # If the main API fails, try the backup API
        ip = requests.get('https://api.ipify.org', timeout=5).text
        response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5).json()
        country_code = response.get('country_code', 'UN')
        CACHED_LOCATION = country_code
        return country_code
        
    except Exception as e:
        print(f"Error getting location: {e}")
        CACHED_LOCATION = 'UN'  # UN as the default value, indicating unknown
        return CACHED_LOCATION

def get_network_speed():
    try:
        # Get initial value
        net1 = psutil.net_io_counters()
        time.sleep(1)  # Wait for 1 second
        # Get final value
        net2 = psutil.net_io_counters()
        # Calculate the rate per second
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
            # Try reading the os-release file for detailed information
            with open('/etc/os-release') as f:
                lines = f.readlines()
                os_info = dict(line.strip().split('=', 1) for line in lines if '=' in line)
                
                # Get the distribution name
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
            
            # If the above method fails, try using the platform module
            dist = platform.dist()
            if dist[0]:
                return dist[0].capitalize()
                
        except:
            # If all else fails, use platform.system()
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
            # If the model name cannot be read, return basic information
            return f"CPU ({psutil.cpu_count()} threads)"
    except Exception as e:
        print(f"Error getting CPU info: {e}")
        return f"CPU ({psutil.cpu_count()} threads)"

def get_all_disks_usage():
    try:
        total_size = 0
        total_used = 0
        # Get all disk partitions
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                # Track all accessible partitions
                usage = psutil.disk_usage(partition.mountpoint)
                total_size += usage.total
                total_used += usage.used
            except (PermissionError, OSError):
                # Skip inaccessible partitions
                continue
                
        # If there is valid disk data
        if total_size > 0:
            # Calculate the overall usage percentage
            usage_percent = (total_used / total_size) * 100
            # Convert to GB
            total_size_gb = total_size / (1024 * 1024 * 1024)
            return usage_percent, total_size_gb
            
        return 0, 0
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return 0, 0

def get_ip_address():
    ipv4 = None
    ipv6 = None
    
    try:
        # Try to get public IPv4
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.ok:
            ipv4 = response.text.strip()
    except Exception as e:
        print(f"Failed to get public IPv4: {e}")
    
    try:
        # Try to get public IPv6
        response = requests.get('https://api6.ipify.org', timeout=5)
        if response.ok:
            ipv6 = response.text.strip()
    except Exception as e:
        print(f"Failed to get public IPv6: {e}")
    
    # Fallback to local IP methods if public IPs are not found
    if not ipv4 or not ipv6:
        if platform.system() == 'Windows':
            try:
                # Get all network interfaces
                addresses = psutil.net_if_addrs()
                for _, addrs in addresses.items():
                    for addr in addrs:
                        # For IPv4
                        if addr.family == socket.AF_INET and not ipv4:
                            if not addr.address.startswith(('127.', '169.254.')):  # Skip localhost and link-local
                                ipv4 = addr.address
                        # For IPv6
                        elif addr.family == socket.AF_INET6 and not ipv6:
                            addr_lower = addr.address.lower()
                            # Skip link-local, unique local addresses and temporary addresses
                            if not (addr_lower.startswith('fe80:') or 
                                  addr_lower.startswith('fc00:') or 
                                  addr_lower.startswith('fd00:') or
                                  ':tmp' in addr_lower):
                                ipv6 = addr.address.split('%')[0]  # Remove scope ID
            except Exception as e:
                print(f"Failed to get local Windows IPs: {e}")
        else:
            # Linux fallback
            try:
                if not ipv4:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 80))
                    ipv4 = s.getsockname()[0]
                    s.close()
                
                if not ipv6:
                    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                    s.connect(('2001:4860:4860::8888', 80))
                    ipv6 = s.getsockname()[0]
                    s.close()
            except Exception as e:
                print(f"Failed to get local IPs: {e}")
    
    # Combine IPv4 and IPv6 if available
    if ipv4 and ipv6:
        return f"{ipv4}/{ipv6}"
    elif ipv4:
        return ipv4
    elif ipv6:
        return ipv6
    
    return '127.0.0.1'

def get_server_info():
    network_in, network_out = get_network_speed()
    memory = psutil.virtual_memory()
    disk_percent, total_disk = get_all_disks_usage()
    
    return {
        'id': SERVER_ID,
        'name': NODE_NAME,
        'type': get_server_type(),
        'location': get_location_from_ip(),
        'ip_address': get_ip_address(),
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
            # Check system model
            for item in w.Win32_ComputerSystem():
                if any(virt in item.Model.lower() for virt in [
                    'virtual', 'vmware', 'kvm', 'xen', 'hyperv'
                ]):
                    return "VPS"
                    
            # Check manufacturer
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
                    'innotek', 'cloud server', 'virtual server', 'vps',
                    'vc2', 'vc2-high-cpu', 'vc2-high-memory',
                    'digitalocean', 'do-regular', 'do-premium',
                    'azure virtual machine', 'azure vm',
                    'aws ec2', 't2.micro', 't3.micro',
                    'gcp instance', 'gce instance',
                    'lightsail', 'elastic compute service',
                    'tencent cloud cvm', 'huawei cloud ecs',
                    'ucloud uhost', 'kingsoft cloud kec',
                    'vagrant', 'docker', 'lxc', 'openvz',
                    'esxi', 'citrix xenserver', 'nutanix ahv',
                    'cloudstack', 'openshift', 'kubernetes',
                    'rackspace cloud', 'ibm cloud virtual server',
                    'upcloud', 'kamatera', 'hostwinds',
                    'time4vps', 'hetzner cloud', 'contabo vps'
                ]
                if any(virt in product_name for virt in virt_products):
                    return "VPS"
                    
            # Method 3: Check CPU info for virtualization flags
            # with open('/proc/cpuinfo') as f:
            #     cpu_info = f.read().lower()
            #     if any(flag in cpu_info for flag in ['vmx', 'svm', 'hypervisor']):
            #         return "VPS"
                    
            # Method 4: Check dmesg for virtualization hints
            try:
                dmesg = subprocess.run(['dmesg'], capture_output=True, text=True).stdout.lower()
                if any(hint in dmesg for hint in ['kvm', 'vmware', 'xen', 'hyperv']):
                    return "VPS"
            except:
                pass
                
        except Exception as e:
            print(f"Error detecting server type: {e}")

    # If all checks fail to detect virtualization features, then it is a physical server
    return "Dedicated Server"

def get_machine_id():
    """Get the unique identifier of the machine"""
    try:
        if platform.system() == "Windows":
            # Windows uses WMI to get the system UUID
            import wmi
            w = wmi.WMI()
            system_info = w.Win32_ComputerSystemProduct()[0]
            return hashlib.md5(system_info.UUID.encode()).hexdigest()
        else:
            # Linux system maintains the original logic
            hostname = socket.gethostname()
            mac = subprocess.check_output("cat /sys/class/net/$(ls /sys/class/net | head -n 1)/address", 
                                       shell=True).decode().strip()
            machine_id = f"{hostname}-{mac}"
            return hashlib.md5(machine_id.encode()).hexdigest()
    except Exception as e:
        print(f"Error getting machine ID: {e}")
        # Use the hostname as a fallback
        return hashlib.md5(socket.gethostname().encode()).hexdigest()

def update_server_with_retry(server_info, max_retries=3, retry_delay=1):
    """Send update with retry mechanism"""
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=server_info, timeout=5)
            if response.status_code == 200:
                print(f"Data uploaded successfully")
                return True
            else:
                print(f"Update failed (attempt {attempt + 1}/{max_retries}): {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    
    return False

sio = Client(
    reconnection=True,
    reconnection_attempts=0,  # 无限重试
    reconnection_delay=1,
    reconnection_delay_max=10,
    randomization_factor=0.5,
    logger=True,  # 启用日志以便调试
    engineio_logger=True
)

# 添加新的接状态跟踪
CONNECTING = False
RETRY_INTERVAL = 5
MAX_CONSECUTIVE_ERRORS = 3
error_count = 0

@sio.event
def connect():
    global CONNECTING, error_count
    print('Connected to server')
    CONNECTING = False
    error_count = 0

@sio.event
def connect_error(error):
    print(f"Connection error: {error}")

@sio.event
def disconnect():
    global CONNECTING
    print('Disconnected from server')
    CONNECTING = False

def get_system_info_buffer():
    """Buffer system information to reduce I/O operations"""
    current_time = time.time()
    if not hasattr(get_system_info_buffer, '_last_full_update'):
        get_system_info_buffer._last_full_update = 0
        get_system_info_buffer._cached_info = None
    
    # Perform a full update every 10 seconds
    if current_time - get_system_info_buffer._last_full_update >= 10:
        system_info = get_server_info()
        # Round all float values to 2 decimal places
        for key, value in system_info.items():
            if isinstance(value, float):
                system_info[key] = round(value, 2)
        
        get_system_info_buffer._cached_info = system_info
        get_system_info_buffer._last_full_update = current_time
        return get_system_info_buffer._cached_info
    
    # Only update frequently changing metrics
    cached_info = get_system_info_buffer._cached_info.copy()
    cached_info.update({
        'cpu': round(psutil.cpu_percent(), 2),
        'memory': round(psutil.virtual_memory().percent, 2),
        'uptime': int(time.time() - psutil.boot_time())
    })
    return cached_info

def connect_with_retry():
    global CONNECTING
    try:
        if not sio.connected and not CONNECTING:
            CONNECTING = True
            print("Attempting to connect...")
            sio.connect(
                API_URL,
                transports=['websocket'],
                wait_timeout=10
            )
    except Exception as e:
        print(f"Connection error: {e}")
        CONNECTING = False
        time.sleep(RETRY_INTERVAL)

def main():
    global NODE_NAME, SERVER_ID, CONNECTING, error_count
    
    NODE_NAME = parse_arguments()
    SERVER_ID = get_machine_id()
    
    print(f"Starting monitoring for server: {SERVER_ID}")
    print(f"Node name: {NODE_NAME}")
    print(f"Sending data to: {API_URL}")
    
    while True:
        try:
            connect_with_retry()
                
            if sio.connected:
                system_info = get_system_info_buffer()

                for key, value in system_info.items():
                    if isinstance(value, (float, int)):
                        system_info[key] = str(value)
                
                sio.emit('server_update', system_info)
                error_count = 0
                
            time.sleep(3)
            
        except Exception as e:
            error_count += 1
            print(f"Error: {e}")
            
            if error_count >= MAX_CONSECUTIVE_ERRORS:
                print(f"Multiple consecutive errors ({error_count}), waiting longer...")
                time.sleep(RETRY_INTERVAL * 2)
                try:
                    if sio.connected:
                        sio.disconnect()
                    CONNECTING = False
                except:
                    pass
                error_count = 0
            else:
                time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if sio.connected:
            sio.disconnect()
        print("\nMonitoring program stopped")
    except Exception as e:
        print(f"Program exited abnormally: {e}")
