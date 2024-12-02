import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import ClientTable from '../../components/admin/ClientTable';
import AddClientModal from '../../components/admin/AddClientModal';
import { Server } from '../../types/server';
import { 
  PlusIcon, 
  ServerIcon, 
  CheckCircleIcon, 
  XCircleIcon 
} from '@heroicons/react/24/outline';
import ProtectedRoute from '../../components/ProtectedRoute';

export default function AdminDashboard() {
  const [clients, setClients] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchClients = async () => {
    try {
      const response = await fetch('http://13.70.189.213:5000/api/servers');
      if (!response.ok) throw new Error('Failed to fetch clients');
      const data = await response.json();
      setClients(data);
      setError(null);
    } catch (error) {
      setError('Error fetching clients');
      console.error('Error fetching clients:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
    const interval = setInterval(fetchClients, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (clientId: string) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await fetch(`http://13.70.189.213:5000/api/servers/${clientId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete server');
      }
      
      await fetchClients();
    } catch (error) {
      console.error('Error deleting server:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete server');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateOrder = async (clientId: string, order: number) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await fetch(`http://13.70.189.213:5000/api/servers/${clientId}/order`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order_index: order })
      });

      if (!response.ok) {
        throw new Error('Failed to update order');
      }
      
      await fetchClients();
    } catch (error) {
      console.error('Error updating order:', error);
      setError(error instanceof Error ? error.message : 'Failed to update order');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClient = async (clientName: string) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await fetch('http://13.70.189.213:5000/api/clients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: clientName })
      });

      if (!response.ok) {
        throw new Error('Failed to add client');
      }
      
      await fetchClients();
    } catch (error) {
      console.error('Error adding client:', error);
      setError(error instanceof Error ? error.message : 'Failed to add client');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <Layout>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Server Management</h1>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Monitor and manage your server clients
                  </p>
                </div>
                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 
                    text-white rounded-md shadow-sm transition-colors duration-200"
                >
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Add Client
                </button>
              </div>

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
                <div className="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-lg p-5 
                  border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow duration-200">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/50">
                      <ServerIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="ml-5">
                      <p className="text-gray-500 dark:text-gray-400 text-sm">Total Clients</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{clients.length}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-lg p-5 
                  border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow duration-200">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/50">
                      <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                    <div className="ml-5">
                      <p className="text-gray-500 dark:text-gray-400 text-sm">Active Clients</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {clients.filter(client => client.status === 'running').length}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-lg p-5 
                  border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow duration-200">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/50">
                      <XCircleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
                    </div>
                    <div className="ml-5">
                      <p className="text-gray-500 dark:text-gray-400 text-sm">Inactive Clients</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {clients.filter(client => client.status !== 'running').length}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {error && (
                <div className="mb-4 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 
                  rounded-lg border border-red-200 dark:border-red-800">
                  {error}
                </div>
              )}

              <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden 
                border border-gray-200 dark:border-gray-700">
                <div className="p-6">
                  <ClientTable 
                    clients={clients} 
                    loading={loading} 
                    onDelete={handleDelete}
                    onUpdateOrder={handleUpdateOrder}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <AddClientModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onAdd={handleAddClient}
        />
      </Layout>
    </ProtectedRoute>
  );
} 