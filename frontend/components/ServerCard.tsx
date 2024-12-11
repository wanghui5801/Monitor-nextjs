import React from 'react';
import { Server } from '../types/server';

interface ServerCardProps {
    server: Server;
    onToggleExpand: (id: string) => void;
}

const ServerCard: React.FC<ServerCardProps> = ({ server, onToggleExpand }) => {
    // Network speed formatting
    const formatNetwork = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B/s`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB/s`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB/s`;
    };

    // Traffic formatting
    const formatTraffic = (bytes: number) => {
        const gb = bytes / (1024 * 1024 * 1024);
        return `${gb.toFixed(2)}G`;
    };

    // Uptime formatting
    const formatUptime = (seconds: number) => {
        const days = Math.floor(seconds / (24 * 60 * 60));
        return `${days} days`;
    };

    const getOsIcon = (osType: string, status: string) => {
        if (status === 'maintenance') {
            return (
                <span className="text-gray-500 dark:text-gray-400 text-sm">
                    Pending
                </span>
            );
        }

        const osLower = osType.toLowerCase();
        if (osLower.includes('ubuntu')) {
            return <img src="https://assets.ubuntu.com/v1/29985a98-ubuntu-logo32.png" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        } else if (osLower.includes('debian')) {
            return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/debian/debian-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        } else if (osLower.includes('centos')) {
            return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/centos/centos-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        } else if (osLower.includes('fedora')) {
            return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fedora/fedora-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        } else if (osLower.includes('redhat') || osLower.includes('rhel')) {
            return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redhat/redhat-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        } else if (osLower.includes('windows')) {
            return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
        }
        
        return <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" alt={osType} className="inline-block w-5 h-5 dark:opacity-80" />;
    };

    const getLocationDisplay = (location: string, status: string) => {
        if (status === 'maintenance') {
            return (
                <span className="text-gray-500 dark:text-gray-400 text-sm">
                    Pending
                </span>
            );
        }

        return (
            <img 
                src={`https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/${(location || 'un').toLowerCase()}.svg`}
                alt={location || 'Unknown'}
                className="inline-block w-8 h-6 rounded-lg hover:scale-110 transition-transform duration-200"
                onError={(e) => {
                    e.currentTarget.src = 'https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/un.svg';
                }}
            />
        );
    };

    const getStatusClass = () => {
        const status = server.status || 'running';
        switch (status) {
            case 'running':
                return 'status-badge-running';
            case 'stopped':
                return 'status-badge-stopped';
            case 'maintenance':
                return 'status-badge-maintenance';
            default:
                return 'status-badge-running';
        }
    };

    const ProgressBar = ({ value, color }: { value: number, color: string }) => {
        const getGradientColor = () => {
            if (server.status === 'maintenance') {
                return 'from-amber-400/90 to-amber-500/90';
            }
            if (server.status === 'stopped') {
                return 'from-red-400/90 to-red-500/90';
            }
            if (value > 80) return 'from-rose-400/90 to-red-400/90';
            if (value > 60) return 'from-amber-400/90 to-yellow-400/90';
            return 'from-emerald-400/90 to-teal-400/90';
        };

        return (
            <div className="flex items-center space-x-2 group">
                <div className="w-10 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div 
                        className={`h-full rounded-full bg-gradient-to-r ${getGradientColor()} 
                        ${value > 80 && server.status === 'running' ? 'animate-pulse-gentle' : ''}`}
                        style={{ width: `${value}%` }}
                    />
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    {value.toFixed(1)}%
                </span>
            </div>
        );
    };

    const formatIpAddress = (ip: string) => {
        if (ip.includes('/')) {
            const [ipv4, ipv6] = ip.split('/');
            return `${ipv4} / ${ipv6}`;
        }
        return ip;
    };

    return (
        <>
            <tr 
                className={`hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors duration-150 cursor-pointer
                    ${server.status && server.status !== 'running' ? 'opacity-75' : ''}`}
                onClick={() => onToggleExpand(server.id)}
            >
                <td className="table-cell">
                    <span className={`status-badge ${getStatusClass()}`}>
                        {(server.status || 'running').charAt(0).toUpperCase() + (server.status || 'running').slice(1)}
                    </span>
                </td>
                <td className="table-cell font-medium text-gray-900 dark:text-white">{server.name}</td>
                <td className="table-cell dark:text-gray-400">{server.type}</td>
                <td className="table-cell text-center">
                    {getLocationDisplay(server.location, server.status)}
                </td>
                <td className="table-cell dark:text-gray-400">{formatUptime(server.uptime)}</td>
                <td className="table-cell dark:text-gray-400">
                    <div className="flex flex-col space-y-1 text-xs">
                        <div className="flex items-center space-x-2">
                            <span className="text-green-500 dark:text-green-400">↓</span>
                            <span>{formatNetwork(server.network_in)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="text-blue-500 dark:text-blue-400">↑</span>
                            <span>{formatNetwork(server.network_out)}</span>
                        </div>
                    </div>
                </td>
                <td className="table-cell w-0">
                    <ProgressBar value={server.cpu} color="bg-blue-500 dark:bg-blue-600" />
                </td>
                <td className="table-cell w-0">
                    <ProgressBar value={server.memory} color="bg-green-500 dark:bg-green-600" />
                </td>
                <td className="table-cell w-0">
                    <ProgressBar value={server.disk} color="bg-yellow-500 dark:bg-yellow-600" />
                </td>
                <td className="table-cell text-center w-30">
                    {getOsIcon(server.os_type, server.status)}
                </td>
            </tr>
            
            {server.is_expanded && (
                <tr className="bg-gray-50/50 dark:bg-gray-800/30">
                    <td colSpan={10} className="px-4 py-3 transition-all duration-200">
                        <div className="grid grid-cols-3 gap-4 text-sm">
                            <div className="space-y-1">
                                <div className="text-gray-500 dark:text-gray-400">CPU Info</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                    {server.cpu_info || 'N/A'}
                                </div>
                            </div>
                            <div className="space-y-1">
                                <div className="text-gray-500 dark:text-gray-400">Total Memory</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                    {server.total_memory ? `${server.total_memory.toFixed(2)} GB` : 'N/A'}
                                </div>
                            </div>
                            <div className="space-y-1">
                                <div className="text-gray-500 dark:text-gray-400">Total Storage</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                    {server.total_disk ? `${server.total_disk.toFixed(2)} GB` : 'N/A'}
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            )}
        </>
    );
};

export default ServerCard;

