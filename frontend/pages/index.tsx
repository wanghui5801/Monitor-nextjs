import Layout from '../components/Layout'
import ServerList from '../components/ServerList'
import { useEffect, useState } from 'react'
import { Server } from '../types/server'
import Link from 'next/link'
import { API_URL } from '../config/config';

export default function Home() {
  const [servers, setServers] = useState<Server[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await fetch(`${API_URL}/api/servers`)
        const data = await response.json()
        setServers(data)
      } catch (error) {
        console.error('Error fetching servers:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchServers()
    const interval = setInterval(fetchServers, 5000)
    return () => clearInterval(interval)
  }, [])

  const getAverageMetrics = () => {
    if (servers.length === 0) return { cpu: 0, memory: 0, disk: 0 }
    return {
      cpu: servers.reduce((acc, server) => acc + server.cpu, 0) / servers.length,
      memory: servers.reduce((acc, server) => acc + server.memory, 0) / servers.length,
      disk: servers.reduce((acc, server) => acc + server.disk, 0) / servers.length,
    }
  }

  const metrics = getAverageMetrics()

  return (
    <Layout>
      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="relative w-16 h-16">
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-200/30 rounded-full animate-spin"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-500/60 rounded-full animate-spin border-t-transparent"></div>
          </div>
          <p className="text-gray-500 dark:text-gray-400 animate-pulse">Loading server data...</p>
        </div>
      ) : (
        <div className="space-y-8 px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="stat-card group">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Servers
                </h3>
                <Link href="/admin">
                  <div className="w-8 h-8 rounded-full bg-blue-50/80 dark:bg-blue-900/30
                    flex items-center justify-center text-blue-500 dark:text-blue-400
                    transform transition-all duration-300 ease-out
                    group-hover:scale-110 group-hover:bg-blue-100/80 dark:group-hover:bg-blue-900/50
                    group-hover:rotate-3">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                        d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              </div>
              <p className="mt-3 text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 
                dark:from-white dark:to-gray-300 bg-clip-text text-transparent
                transition-all duration-300">
                {servers.length}
              </p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average CPU</h3>
              <p className="mt-2 text-3xl font-semibold bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent">
                {metrics.cpu.toFixed(1)}%
              </p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Memory</h3>
              <p className="mt-2 text-3xl font-semibold bg-gradient-to-r from-green-600 to-green-400 dark:from-green-400 dark:to-green-300 bg-clip-text text-transparent">
                {metrics.memory.toFixed(1)}%
              </p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Disk</h3>
              <p className="mt-2 text-3xl font-semibold bg-gradient-to-r from-yellow-600 to-yellow-400 dark:from-yellow-400 dark:to-yellow-300 bg-clip-text text-transparent">
                {metrics.disk.toFixed(1)}%
              </p>
            </div>
          </div>
          <ServerList servers={servers} />
        </div>
      )}
    </Layout>
  )
}