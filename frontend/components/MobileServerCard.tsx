import React from 'react';
import { Server } from '../types/server';

interface MobileServerCardProps {
  server: Server;
  onToggleExpand: (id: string) => void;
}

const MobileServerCard: React.FC<MobileServerCardProps> = ({ server, onToggleExpand }) => {
  const formatNetwork = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B/s`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB/s`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB/s`;
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 60 * 60));
    return `${days} days`;
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

  const ProgressBar = ({ value, label }: { value: number; label: string }) => {
    const getGradientColor = () => {
      if (server.status === 'maintenance') return 'from-amber-400/90 to-amber-500/90';
      if (server.status === 'stopped') return 'from-red-400/90 to-red-500/90';
      if (value > 80) return 'from-rose-400/90 to-red-400/90';
      if (value > 60) return 'from-amber-400/90 to-yellow-400/90';
      return 'from-emerald-400/90 to-teal-400/90';
    };

    return (
      <div className="flex flex-col space-y-1">
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-600 dark:text-gray-400">{label}</span>
          <span className="text-gray-900 dark:text-gray-100">{value.toFixed(1)}%</span>
        </div>
        <div className="progress-bar-container h-2">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${getGradientColor()} 
            ${value > 80 && server.status === 'running' ? 'animate-pulse-gentle' : ''}`}
            style={{ width: `${value}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div 
      className="bg-white/90 dark:bg-gray-800/90 rounded-xl shadow-md p-5 space-y-4 
        border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-sm
        hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]
        transition-all duration-200"
      onClick={() => onToggleExpand(server.id)}
    >
      {/* First Row */}
      <div className="flex items-center justify-between">
        <span className={`status-badge ${getStatusColor()}`}>
          {(server.status || 'running').charAt(0).toUpperCase() + (server.status || 'running').slice(1)}
        </span>
        <span className="font-medium text-gray-900 dark:text-white">{server.name}</span>
        <span className="text-sm text-gray-500 dark:text-gray-400">{server.type}</span>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="text-center">
          <div className="text-gray-500 dark:text-gray-400 text-xs mb-1">Location</div>
          <img 
            src={`https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/${(server.location || 'un').toLowerCase()}.svg`}
            alt={server.location || 'Unknown'}
            className="w-6 h-4 mx-auto rounded hover:scale-110 transition-transform duration-200"
            onError={(e) => {
              e.currentTarget.src = 'https://cdn.jsdelivr.net/gh/xykt/ISO3166@main/flags/svg/un.svg';
            }}
          />
        </div>
        <div className="text-center">
          <div className="text-gray-500 dark:text-gray-400 text-xs mb-1">Uptime</div>
          <div className="text-gray-900 dark:text-gray-100">{formatUptime(server.uptime)}</div>
        </div>
        <div className="text-center">
          <div className="text-gray-500 dark:text-gray-400 text-xs mb-1">Network</div>
          <div className="flex flex-col text-xs">
            <span className="text-green-500">↓ {formatNetwork(server.network_in)}</span>
            <span className="text-blue-500">↑ {formatNetwork(server.network_out)}</span>
          </div>
        </div>
      </div>

      {/* Third Row */}
      <div className="space-y-2">
        <ProgressBar value={server.cpu} label="CPU" />
        <ProgressBar value={server.memory} label="Memory" />
        <ProgressBar value={server.disk} label="Disk" />
      </div>

      {/* Expanded Details */}
      {server.is_expanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 gap-4 text-sm">
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
        </div>
      )}
    </div>
  );
};

export default MobileServerCard; 