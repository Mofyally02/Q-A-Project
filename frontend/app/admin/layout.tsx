'use client'

import { ThemeProvider } from '../client/components/ThemeProvider'
import { Toaster } from 'react-hot-toast'
import dynamic from 'next/dynamic'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

// Dynamically import heavy components to reduce initial bundle
const AdminSidebar = dynamic(() => import('@/components/admin/AdminSidebar').then(mod => ({ default: mod.AdminSidebar })), {
  ssr: true, // Keep SSR for layout components
  loading: () => <div className="w-20 lg:w-64 h-screen bg-background border-r border-border" />
})
const AdminHeader = dynamic(() => import('@/components/admin/AdminHeader').then(mod => ({ default: mod.AdminHeader })), {
  ssr: true, // Keep SSR for layout components
  loading: () => <div className="h-16 bg-background border-b border-border" />
})

function AdminAppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarExpanded, setSidebarExpanded] = useState(false)

  useEffect(() => {
    let observer: MutationObserver | null = null
    let sidebar: Element | null = null
    let cleanup: (() => void) | null = null
    
    // Check if sidebar is expanded on desktop
    const checkSidebar = () => {
      if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
        // On desktop, sidebar can be expanded via hover
        // Look for the desktop sidebar specifically (not mobile)
        sidebar = document.querySelector('aside.hidden.lg\\:flex')
        if (sidebar) {
          // Clean up previous observer if exists
          if (observer) {
            observer.disconnect()
          }
          
          observer = new MutationObserver(() => {
            const isExpanded = sidebar?.classList.contains('w-64') || false
            setSidebarExpanded(isExpanded)
          })
          observer.observe(sidebar, {
            attributes: true,
            attributeFilter: ['class'],
            attributeOldValue: false
          })
          // Initial check
          setSidebarExpanded(sidebar.classList.contains('w-64'))
          
          // Also listen for mouse events on the sidebar for immediate response
          const handleMouseEnter = () => setSidebarExpanded(true)
          const handleMouseLeave = () => setSidebarExpanded(false)
          
          sidebar.addEventListener('mouseenter', handleMouseEnter)
          sidebar.addEventListener('mouseleave', handleMouseLeave)
          
          cleanup = () => {
            if (observer) {
              observer.disconnect()
            }
            if (sidebar) {
              sidebar.removeEventListener('mouseenter', handleMouseEnter)
              sidebar.removeEventListener('mouseleave', handleMouseLeave)
            }
          }
        }
      } else {
        setSidebarExpanded(false)
      }
    }
    
    // Delay to ensure DOM is ready
    const timer = setTimeout(checkSidebar, 100)
    window.addEventListener('resize', checkSidebar)
    
    return () => {
      clearTimeout(timer)
      window.removeEventListener('resize', checkSidebar)
      if (cleanup) {
        cleanup()
      }
    }
  }, [])

  return (
    <div className="flex min-h-screen bg-background">
      <AdminSidebar />
      <main className={cn(
        "flex-1 flex flex-col transition-all duration-300 ease-in-out",
        // Mobile: no margin (sidebar is overlay)
        // Desktop: Match sidebar width exactly: 256px (w-64) when expanded, 80px (w-20) when collapsed
        sidebarExpanded ? "lg:ml-[256px]" : "lg:ml-[80px]",
        // Add top padding on mobile for menu button
        "pt-16 lg:pt-0"
      )}>
        <AdminHeader />
        <div className="flex-1 overflow-y-auto">
          {/* Content area - matches reference layout */}
          <div className="p-6 lg:p-8 w-full">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AdminAppLayout>
        {children}
      </AdminAppLayout>
      <Toaster position="bottom-right" />
    </ThemeProvider>
  )
}
