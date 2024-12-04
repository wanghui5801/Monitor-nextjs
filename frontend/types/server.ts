export interface Server {
    id: string;
    name: string;
    type: string;
    location: string;
    ip_address: string;
    status: string;
    uptime: number;
    network_in: number;
    network_out: number;
    cpu: number;
    memory: number;
    disk: number;
    os_type: string;
    order_index: number;
    last_update: string;
    cpu_info: string;
    total_memory: number;
    total_disk: number;
    is_expanded?: boolean;
}
