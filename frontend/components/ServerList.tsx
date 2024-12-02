import React, { useEffect, useState } from 'react';
import { Server } from '../types/server';
import ServerCard from './ServerCard';
import TableHeader from './TableHeader';

interface ServerListProps {
  servers: Server[];
}

const ServerList: React.FC<ServerListProps> = ({ servers }) => {
  // 按 order_index 排序服务器
  const sortedServers = [...servers].sort((a, b) => 
    (b.order_index || 0) - (a.order_index || 0)
  );

  return (
    <div className="server-table w-full">
      <div className="overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200/20 dark:divide-gray-700/20">
          <thead>
            <TableHeader />
          </thead>
          <tbody className="divide-y divide-gray-200/20 dark:divide-gray-700/20">
            {sortedServers.map(server => (
              <ServerCard key={server.id} server={server} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ServerList;
