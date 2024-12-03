import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import ResetPasswordModal from './ResetPasswordModal';
import { useAuth } from '../../hooks/useAuth';

const AdminNav = () => {
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);
  const router = useRouter();
  const { logout } = useAuth();
  
  return (
    <nav className="bg-white dark:bg-gray-800 shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/admin" className="text-xl font-bold text-gray-900 dark:text-white">
                Admin Dashboard
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link href="/admin" 
                className={`${
                  router.pathname === '/admin'
                    ? 'border-blue-500 text-gray-900 dark:text-white'
                    : 'border-transparent text-gray-500 dark:text-gray-400'
                } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}>
                Overview
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsResetModalOpen(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 
                hover:bg-blue-700 rounded-md transition-colors duration-200"
            >
              Reset Password
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300
                hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
      <ResetPasswordModal 
        isOpen={isResetModalOpen}
        onClose={() => setIsResetModalOpen(false)}
      />
    </nav>
  );
};

export default AdminNav; 