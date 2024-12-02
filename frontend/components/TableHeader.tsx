const TableHeader = () => {
  return (
    <tr className="bg-gradient-to-r from-gray-50/80 to-gray-50/80 
      dark:from-gray-800/80 dark:to-gray-800/80">
      <th className="px-4 py-3.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 
        uppercase tracking-wider w-24 first:rounded-tl-lg">
        <div className="flex items-center space-x-1">
          <span>Status</span>
        </div>
      </th>
      <th className="px-4 py-3.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 
        uppercase tracking-wider w-32">
        Node Name
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-20 bg-gray-50/80 dark:bg-gray-800/80">
        Type
      </th>
      <th className="px-4 py-3 text-center text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-24 bg-gray-50/80 dark:bg-gray-800/80">
        Location
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-24 bg-gray-50/80 dark:bg-gray-800/80">
        Uptime
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-32 bg-gray-50/80 dark:bg-gray-800/80">
        Network(B/s)
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-24 bg-gray-50/80 dark:bg-gray-800/80">
        CPU
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-24 bg-gray-50/80 dark:bg-gray-800/80">
        Memory
      </th>
      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-24 bg-gray-50/80 dark:bg-gray-800/80">
        Disk
      </th>
      <th className="px-4 py-3 text-center text-xs font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-20 bg-gray-50/80 dark:bg-gray-800/80 last:rounded-tr-lg">
        OS Type
      </th>
    </tr>
  );
};

export default TableHeader;
