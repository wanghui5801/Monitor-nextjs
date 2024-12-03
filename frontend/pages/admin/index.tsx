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
import AdminStats from '../../components/admin/AdminStats';
import ResetPasswordModal from '../../components/admin/ResetPasswordModal';
import { useAuth } from '../../hooks/useAuth';
import { Toaster } from 'react-hot-toast';

export default function AdminDashboard() {
  const { logout } = useAuth();
  const [clients, setClients] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);

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
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#333',
              color: '#fff',
            },
          }}
        />
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
                Client Management
              </h1>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsResetModalOpen(true)}
                  className="inline-flex items-center px-4 py-2
                    bg-blue-600 hover:bg-blue-700 
                    dark:bg-blue-500 dark:hover:bg-blue-600
                    text-white rounded-lg shadow-sm
                    transition-all duration-200 hover:scale-105"
                >
                  Reset Password
                </button>
                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 space-x-2
                    bg-blue-600 hover:bg-blue-700 
                    dark:bg-blue-500 dark:hover:bg-blue-600
                    text-white rounded-lg shadow-sm
                    transition-all duration-200 hover:scale-105"
                >
                  <PlusIcon className="h-5 w-5" />
                  <span>Add Client</span>
                </button>
                <button
                  onClick={logout}
                  className="inline-flex items-center px-4 py-2
                    bg-gray-600 hover:bg-gray-700 
                    dark:bg-gray-500 dark:hover:bg-gray-600
                    text-white rounded-lg shadow-sm
                    transition-all duration-200 hover:scale-105"
                >
                  Logout
                </button>
              </div>
            </div>

            <div className="space-y-6">
              <AdminStats clients={clients} />
              <div className="bg-white/90 dark:bg-gray-800/90 
                shadow-lg rounded-xl border border-gray-200/50 
                dark:border-gray-700/50 backdrop-blur-sm">
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
        <AddClientModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onAdd={handleAddClient}
        />
        <ResetPasswordModal
          isOpen={isResetModalOpen}
          onClose={() => setIsResetModalOpen(false)}
        />
      </Layout>
    </ProtectedRoute>
  );
} 