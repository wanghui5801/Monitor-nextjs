import Link from 'next/link';
import { useRouter } from 'next/router';

const AdminNav = () => {
  const router = useRouter();
  
  return (
    <div className="bg-white dark:bg-gray-800 shadow">
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
              <Link href="/admin/clients"
                className="border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300
                inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Clients
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminNav; 