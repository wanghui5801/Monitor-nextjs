import Head from 'next/head'
import Navbar from './Navbar'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 
      dark:from-gray-900 dark:to-gray-800 transition-colors duration-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(45%_25%_at_50%_50%,rgba(56,189,248,0.05),rgba(255,255,255,0))]
        dark:bg-[radial-gradient(45%_25%_at_50%_50%,rgba(56,189,248,0.05),rgba(0,0,0,0))]" />
      <Navbar />
      <div className="pt-16 pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="relative">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Layout 