import { Server } from '../../types/server';
import { AdminStats as AdminStatsType } from '../../types/admin';
import { ServerIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface AdminStatsProps {
  clients: Server[];
}

const AdminStats = ({ clients }: AdminStatsProps) => {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div className="metric-card">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Total Clients
          </h3>
          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 
            flex items-center justify-center">
            <ServerIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <p className="metric-value mt-2">{clients.length}</p>
      </div>
      
      {/* Active Clients Card */}
      <div className="metric-card">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Active Clients
          </h3>
          <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/50 
            flex items-center justify-center">
            <CheckCircleIcon className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
        </div>
        <p className="metric-value mt-2 !from-emerald-600 !to-emerald-400 
          dark:!from-emerald-400 dark:!to-emerald-300">
          {clients.filter(client => client.status === 'running').length}
        </p>
      </div>
    </div>
  );
};

export default AdminStats; 