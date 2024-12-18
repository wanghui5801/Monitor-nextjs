import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { API_URL } from '../config/config';

export default function Login() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/admin');
      return;
    }
    
    const checkInitialization = async () => {
      try {
        const response = await fetch(`${API_URL}/api/auth/status`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        const data = await response.json();
        setIsInitializing(!data.initialized);
      } catch (error) {
        console.error('Error checking initialization:', error);
        setIsInitializing(true);
      }
    };

    checkInitialization();
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      if (isInitializing) {
        const initRes = await fetch(`${API_URL}/api/auth/initialize`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ password })
        });
        
        if (!initRes.ok) {
          throw new Error('Failed to initialize');
        }
        
        await login(password);
        router.push('/admin');
      } else {
        await login(password);
        router.push('/admin');
      }
    } catch (err) {
      setError('Invalid password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            {isInitializing ? 'Set Admin Password' : 'Admin Login'}
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="password" className="sr-only">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 
                border border-gray-300 dark:border-gray-700 placeholder-gray-500 
                text-gray-900 dark:text-white bg-white dark:bg-gray-800 
                focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 
                border border-transparent text-sm font-medium rounded-md 
                text-white bg-blue-600 hover:bg-blue-700 focus:outline-none 
                focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {isInitializing ? 'Set Password' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
