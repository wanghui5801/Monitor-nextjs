import React, { useState } from 'react';
import { Server } from '../types/server';
import ServerCard from './ServerCard';
import TableHeader from './TableHeader';
import MobileServerCard from './MobileServerCard';

interface ServerListProps {
  servers: Server[];
}

const ServerList: React.FC<ServerListProps> = ({ servers }) => {
  const [expandedServers, setExpandedServers] = useState<Set<string>>(new Set());

  const handleToggleExpand = (serverId: string) => {
    setExpandedServers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(serverId)) {
        newSet.delete(serverId);
      } else {
        newSet.add(serverId);
      }
      return newSet;
    });
  };

  const sortedServers = [...servers].sort((a, b) => 
    (b.order_index || 0) - (a.order_index || 0)
  ).map(server => ({
    ...server,
    is_expanded: expandedServers.has(server.id)
  }));

  return (
    <div className="w-full">
      {/* Desktop View */}
      <div className="hidden md:block">
        <div className="overflow-hidden bg-white/90 dark:bg-gray-800/90 
          shadow-lg rounded-xl border border-gray-200/50 
          dark:border-gray-700/50 backdrop-blur-sm
          transition-all duration-300">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <TableHeader />
            </thead>
            <tbody>
              {sortedServers.map(server => (
                <ServerCard 
                  key={server.id} 
                  server={server}
                  onToggleExpand={handleToggleExpand}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile View */}
      <div className="md:hidden grid gap-4">
        {sortedServers.map(server => (
          <MobileServerCard
            key={server.id}
            server={server}
            onToggleExpand={handleToggleExpand}
          />
        ))}
      </div>
    </div>
  );
};

export default ServerList;
