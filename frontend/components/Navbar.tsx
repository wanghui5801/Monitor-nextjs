import { useTheme } from 'next-themes'
import Link from 'next/link'
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'

const Navbar = () => {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // 等待挂载完成后再渲染,避免水合错误
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/60 dark:bg-gray-800/60 border-b 
      border-gray-200/50 dark:border-gray-700/50 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2 group">
              <div className="text-blue-600 dark:text-blue-400 transition-transform duration-300 
                group-hover:scale-110">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 
                dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                Server Monitor
              </span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-lg bg-gray-100/80 dark:bg-gray-700/80 hover:bg-gray-200/80 
                dark:hover:bg-gray-600/80 transition-all duration-300 hover:scale-105"
              aria-label="Toggle dark mode"
            >
              {theme === 'dark' ? (
                <SunIcon className="w-5 h-5 text-amber-500" />
              ) : (
                <MoonIcon className="w-5 h-5 text-blue-600" />
              )}
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar 