import Head from 'next/head'
import Navbar from './Navbar'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="relative pt-16">
        {children}
      </main>
    </div>
  )
}

export default Layout 