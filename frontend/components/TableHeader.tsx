const TableHeader = () => {
  return (
    <tr className="bg-gradient-to-r from-gray-50/80 to-gray-50/80 
      dark:from-gray-800/80 dark:to-gray-800/80">
      <th className="table-cell text-left text-[11px] font-medium text-gray-500 dark:text-gray-400 
        uppercase tracking-wider w-12">
        <div className="flex items-center space-x-1">
          <span>Status</span>
        </div>
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-500 dark:text-gray-400 
        uppercase tracking-wider w-12">
        Node Name
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-12">
        Type
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-12">
        Location
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-12">
        Uptime
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-12">
        Network(B/s)
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-4">
        CPU
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-4">
        Memory
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-1">
        Disk
      </th>
      <th className="table-cell text-left text-[11px] font-medium text-gray-600 dark:text-gray-300 
        uppercase tracking-wider w-1 pl-2">
        OS Type
      </th>
    </tr>
  );
};

export default TableHeader;
