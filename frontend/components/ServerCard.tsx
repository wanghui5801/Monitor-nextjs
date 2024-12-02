import React from 'react';
import { Server } from '../types/server';

interface ServerCardProps {
    server: Server;
}

const ServerCard: React.FC<ServerCardProps> = ({ server }) => {
    const formatNetwork = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B/s`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB/s`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB/s`;
    };

    const formatTraffic = (bytes: number) => {
        const gb = bytes / (1024 * 1024 * 1024);
        return `${gb.toFixed(2)}G`;
    };

    const formatUptime = (seconds: number) => {
        const days = Math.floor(seconds / (24 * 60 * 60));
        return `${days} days`;
    };

    const getOsIcon = (osType: string) => {
        const osLower = osType.toLowerCase();
        
        if (osLower.includes('ubuntu')) {
            return 'https://assets.ubuntu.com/v1/29985a98-ubuntu-logo32.png';
        } else if (osLower.includes('debian')) {
            return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/debian/debian-original.svg';
        } else if (osLower.includes('centos')) {
            return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/centos/centos-original.svg';
        } else if (osLower.includes('fedora')) {
            return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fedora/fedora-original.svg';
        } else if (osLower.includes('redhat') || osLower.includes('rhel')) {
            return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redhat/redhat-original.svg';
        } else if (osLower.includes('windows')) {
            return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg';
        }
        
        return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg';
    };

    const getStatusColor = () => {
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
                return 'from-yellow-400 to-amber-500';
            }
            if (server.status === 'stopped') {
                return 'from-red-400 to-red-500';
            }
            if (value > 80) return 'from-rose-400 to-red-400';
            if (value > 60) return 'from-amber-400 to-yellow-400';
            return 'from-emerald-400 to-teal-400';
        };

        return (
            <div className="progress-bar-wrapper group">
                <div className={`progress-bar-container ${server.status !== 'running' ? 'opacity-75' : ''}`}>
                    <div 
                        className={`progress-bar bg-gradient-to-r ${getGradientColor()} 
                        ${value > 80 && server.status === 'running' ? 'animate-pulse-gentle' : ''}`}
                        style={{ width: `${value}%` }}
                    >
                        <div className="absolute inset-0 bg-white/5 rounded-full"></div>
                    </div>
                </div>
                <span className="metric-text group-hover:opacity-100 transition-all duration-300">
                    {value.toFixed(1)}%
                </span>
            </div>
        );
    };

    return (
        <tr className={`hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors duration-150
            ${server.status && server.status !== 'running' ? 'opacity-75' : ''}`}>
            <td className="table-cell">
                <span className={`status-badge ${getStatusColor()}`}>
                    {(server.status || 'running').charAt(0).toUpperCase() + (server.status || 'running').slice(1)}
                </span>
            </td>
            <td className="table-cell font-medium text-gray-900 dark:text-white">{server.name}</td>
            <td className="table-cell dark:text-gray-400">{server.type}</td>
            <td className="table-cell text-center">
                <img 
                    src={`https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/${(server.location || 'un').toLowerCase()}.svg`}
                    alt={server.location || 'Unknown'}
                    className="inline-block w-8 h-6 rounded-lg hover:scale-110 transition-transform duration-200"
                    onError={(e) => {
                        e.currentTarget.src = 'https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/un.svg';
                    }}
                />
            </td>
            <td className="table-cell dark:text-gray-400">{formatUptime(server.uptime)}</td>
            <td className="table-cell dark:text-gray-400">
                {formatNetwork(server.network_in)} | {formatNetwork(server.network_out)}
            </td>
            <td className="table-cell">
                <ProgressBar value={server.cpu} color="bg-blue-500 dark:bg-blue-600" />
            </td>
            <td className="table-cell">
                <ProgressBar value={server.memory} color="bg-green-500 dark:bg-green-600" />
            </td>
            <td className="table-cell">
                <ProgressBar value={server.disk} color="bg-yellow-500 dark:bg-yellow-600" />
            </td>
            <td className="table-cell text-center">
                <img 
                    src={getOsIcon(server.os_type)}
                    alt={server.os_type}
                    className="inline-block w-5 h-5 dark:opacity-80"
                />
            </td>
        </tr>
    );
};

export default ServerCard;

