import { Server } from '../../types/server';
import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

interface ClientTableProps {
  clients: Server[];
  loading: boolean;
  onDelete: (clientId: string) => void;
  onUpdateOrder: (clientId: string, order: number) => void;
}

const ClientTable: React.FC<ClientTableProps> = ({ clients, loading, onDelete, onUpdateOrder }) => {
  const [editingOrder, setEditingOrder] = useState<{id: string, value: string}>({id: '', value: ''});

  const handleOrderChange = (clientId: string, value: string) => {
    setEditingOrder({id: clientId, value});
  };

  const handleOrderSubmit = (clientId: string) => {
    const orderValue = parseInt(editingOrder.value);
    if (!isNaN(orderValue)) {
      onUpdateOrder(clientId, orderValue);
    }
    setEditingOrder({id: '', value: ''});
  };

  const copyToClipboard = useCallback(async (text: string) => {
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      
      textArea.select();
      
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        document.execCommand('copy');
      }
      
      document.body.removeChild(textArea);
      toast.success('Command copied to clipboard!');
    } catch (err) {
      console.error('Copy failed:', err);
      toast.error('Failed to copy command. Please copy manually.');
    }
  }, []);

  const getLinuxCommand = (clientName: string) => {
    return `wget -O install.sh https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.sh && chmod +x install.sh && sudo ./install.sh "${clientName}"`;
  };

  const getWindowsCommand = (clientName: string) => {
    return `powershell -Command "& { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/wanghui5801/Monitor-nextjs/main/install_client.bat' -OutFile 'install_client.bat'; Start-Process -FilePath 'install_client.bat' -ArgumentList '${clientName}' -Verb RunAs }"`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Order
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Name
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Location
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Type
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Install Commands
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
          {clients.map((client) => (
            <tr key={client.id}>
              <td className="px-6 py-4 whitespace-nowrap">
                {editingOrder.id === client.id ? (
                  <div className="flex items-center space-x-2">
                    <input
                      type="number"
                      value={editingOrder.value}
                      onChange={(e) => handleOrderChange(client.id, e.target.value)}
                      className="w-20 px-2 py-1 border rounded dark:bg-gray-800 dark:border-gray-700"
                    />
                    <button
                      onClick={() => handleOrderSubmit(client.id)}
                      className="text-green-600 hover:text-green-900 dark:text-green-400"
                    >
                      ✓
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => setEditingOrder({id: client.id, value: String(client.order_index || 0)})}
                    className="cursor-pointer hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    {client.order_index || 0}
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <button
                  onClick={() => onDelete(client.id)}
                  className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{client.name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{client.location}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{client.type}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => copyToClipboard(getLinuxCommand(client.name))}
                    className="inline-flex items-center px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors duration-200"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Copy Linux Install
                  </button>
                  <button
                    onClick={() => copyToClipboard(getWindowsCommand(client.name))}
                    className="inline-flex items-center px-3 py-1 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Copy Windows Install
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ClientTable; 