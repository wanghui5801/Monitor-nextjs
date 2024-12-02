import Layout from '../components/Layout'
import ServerList from '../components/ServerList'
import { useEffect, useState } from 'react'
import { Server } from '../types/server'
import Link from 'next/link'

export default function Home() {
  const [servers, setServers] = useState<Server[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await fetch('http://13.70.189.213:5000/api/servers')
        const data = await response.json()
        setServers(data)
      } catch (error) {
        console.error('Error fetching servers:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchServers()
    const interval = setInterval(fetchServers, 2000)
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
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-200 rounded-full animate-spin"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-500 rounded-full animate-spin border-t-transparent"></div>
          </div>
          <p className="text-gray-500 dark:text-gray-400">Loading server data...</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="stat-card group">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Servers
                </h3>
                <Link href="/admin">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-50 to-blue-100
                    dark:from-blue-900/30 dark:to-blue-800/30
                    flex items-center justify-center text-blue-500 dark:text-blue-400
                    group-hover:scale-110 transition-all duration-300 shadow-sm
                    cursor-pointer hover:from-blue-100 hover:to-blue-200
                    dark:hover:from-blue-800/30 dark:hover:to-blue-700/30">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                        d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              </div>
              <p className="mt-3 text-3xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-800 
                dark:from-gray-100 dark:via-gray-200 dark:to-gray-300 bg-clip-text text-transparent">
                {servers.length}
              </p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average CPU</h3>
              <p className="mt-2 text-3xl font-semibold text-blue-600 dark:text-blue-400">{metrics.cpu.toFixed(1)}%</p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Memory</h3>
              <p className="mt-2 text-3xl font-semibold text-green-600 dark:text-green-400">{metrics.memory.toFixed(1)}%</p>
            </div>
            <div className="stat-card">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Disk</h3>
              <p className="mt-2 text-3xl font-semibold text-yellow-600 dark:text-yellow-400">{metrics.disk.toFixed(1)}%</p>
            </div>
          </div>
          <ServerList servers={servers} />
        </div>
      )}
    </Layout>
  )
}
