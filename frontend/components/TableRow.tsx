interface TableRowProps {
  status: string;
  name: string;
  type: string;
  location: string;
  uptime: number;
  load: number;
  networkIn: number;
  networkOut: number;
  trafficIn: number;
  trafficOut: number;
  cpu: number;
  memory: number;
  disk: number;
  osType: string;
}

const TableRow = ({ ...props }: TableRowProps) => {
  const formatUptime = (uptime: number) => {
    const days = Math.floor(uptime / (24 * 3600));
    return `${days} days`;
  };

  const formatNetwork = (bytes: number) => {
    return `${(bytes / 1024).toFixed(2)} KB/s`;
  };

  const formatTraffic = (bytes: number) => {
    return `${(bytes).toFixed(2)}G`;
  };

  return (
    <tr className="border-b border-gray-100 dark:border-gray-700/50 
      hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-all duration-200">
      <td className="table-cell">
        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium
          bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300
          ring-1 ring-emerald-200/50 dark:ring-emerald-800/50
          transition-all duration-200 hover:bg-emerald-100/80 dark:hover:bg-emerald-800/40">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse"></span>
          <span>Running</span>
        </span>
      </td>
      
      <td className="table-cell group">
        <span className="font-medium text-gray-900 dark:text-white transition-colors duration-200
          group-hover:text-blue-600 dark:group-hover:text-blue-400">{props.name}</span>
      </td>
      
      <td className="table-cell">
        <div className="flex flex-col space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <span className="text-green-500 dark:text-green-400">↓</span>
            <span>{formatNetwork(props.networkIn)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-blue-500 dark:text-blue-400">↑</span>
            <span>{formatNetwork(props.networkOut)}</span>
          </div>
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`fi fi-${props.location.toLowerCase()}`}></span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatUptime(props.uptime)}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{props.load.toFixed(2)}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {formatTraffic(props.trafficIn)} | {formatTraffic(props.trafficOut)}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center group">
          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 shadow-inner overflow-hidden">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                props.cpu > 80 ? 'bg-red-500 dark:bg-red-600' :
                props.cpu > 60 ? 'bg-yellow-500 dark:bg-yellow-600' :
                'bg-green-500 dark:bg-green-600'
              }`} 
              style={{width: `${props.cpu}%`}}
            />
          </div>
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors duration-200">
            {props.cpu.toFixed(1)}%
          </span>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center group">
          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 shadow-inner overflow-hidden">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                props.memory > 80 ? 'bg-red-500 dark:bg-red-600' :
                props.memory > 60 ? 'bg-yellow-500 dark:bg-yellow-600' :
                'bg-green-500 dark:bg-green-600'
              }`} 
              style={{width: `${props.memory}%`}}
            />
          </div>
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors duration-200">
            {props.memory.toFixed(1)}%
          </span>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center group">
          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 shadow-inner overflow-hidden">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                props.disk > 80 ? 'bg-red-500 dark:bg-red-600' :
                props.disk > 60 ? 'bg-yellow-500 dark:bg-yellow-600' :
                'bg-green-500 dark:bg-green-600'
              }`} 
              style={{width: `${props.disk}%`}}
            />
          </div>
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors duration-200">
            {props.disk.toFixed(1)}%
          </span>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <i className={`fab fa-${props.osType.toLowerCase()}`}></i>
      </td>
    </tr>
  );
};

export default TableRow; 