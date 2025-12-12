'use client'

import { ThemeProvider } from './components/ThemeProvider'
import { Toaster } from 'react-hot-toast'
import dynamic from 'next/dynamic'
import { useState, useEffect, createContext, useContext } from 'react'
import { cn } from '@/lib/utils'

// Context for sidebar state
const SidebarContext = createContext<{
  isExpanded: boolean
  setIsExpanded: (expanded: boolean) => void
}>({
  isExpanded: false,
  setIsExpanded: () => {}
})

export const useSidebar = () => useContext(SidebarContext)

// Dynamically import heavy components to reduce initial bundle
const ClientSidebar = dynamic(() => import('@/components/client/ClientSidebar').then(mod => ({ default: mod.ClientSidebar })), {
  ssr: true, // Keep SSR for layout components
  loading: () => <div className="w-20 lg:w-64 h-screen bg-background border-r border-border" />
})
const ClientHeader = dynamic(() => import('@/components/client/ClientHeader').then(mod => ({ default: mod.ClientHeader })), {
  ssr: true, // Keep SSR for layout components
  loading: () => <div className="h-16 bg-background border-b border-border" />
})

function ClientAppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarExpanded, setSidebarExpanded] = useState(false)

  useEffect(() => {
    let sidebar: Element | null = null
    let observer: MutationObserver | null = null
    let handleMouseEnter: (() => void) | null = null
    let handleMouseLeave: (() => void) | null = null
    
    const updateSidebarState = () => {
      if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
        sidebar = document.querySelector('aside.hidden.lg\\:flex')
        if (sidebar) {
          // Check data-expanded attribute first, then fallback to class
          const dataExpanded = sidebar.getAttribute('data-expanded')
          const isExpanded = dataExpanded === 'true' || sidebar.classList.contains('w-64')
          setSidebarExpanded(isExpanded)
        }
      } else {
        setSidebarExpanded(false)
      }
    }
    
    // Initial check with delay
    const timer = setTimeout(() => {
      sidebar = document.querySelector('aside.hidden.lg\\:flex')
      if (sidebar) {
        // Use MutationObserver to watch for attribute and class changes
        observer = new MutationObserver(() => {
          updateSidebarState()
        })
        
        observer.observe(sidebar, {
          attributes: true,
          attributeFilter: ['data-expanded', 'class'],
          subtree: false
        })
        
        // Initial state check
        updateSidebarState()
        
        // Also listen for mouse events for immediate response
        handleMouseEnter = () => {
          if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
            setSidebarExpanded(true)
          }
        }
        
        handleMouseLeave = () => {
          if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
            setSidebarExpanded(false)
          }
        }
        
        sidebar.addEventListener('mouseenter', handleMouseEnter)
        sidebar.addEventListener('mouseleave', handleMouseLeave)
      }
    }, 100)
    
    // Also listen for resize
    window.addEventListener('resize', updateSidebarState)
    
    return () => {
      clearTimeout(timer)
      if (observer) {
        observer.disconnect()
      }
      if (sidebar && handleMouseEnter && handleMouseLeave) {
        sidebar.removeEventListener('mouseenter', handleMouseEnter)
        sidebar.removeEventListener('mouseleave', handleMouseLeave)
      }
      window.removeEventListener('resize', updateSidebarState)
    }
  }, [])

  return (
    <SidebarContext.Provider value={{ isExpanded: sidebarExpanded, setIsExpanded: setSidebarExpanded }}>
      <div className="flex min-h-screen bg-background">
        <ClientSidebar />
        <main className={cn(
          "flex-1 flex flex-col transition-[margin-left] duration-300 ease-in-out",
          // Mobile: no margin (sidebar is overlay)
          // Desktop: Match sidebar width exactly: 256px (w-64) when expanded, 80px (w-20) when collapsed
          sidebarExpanded ? "lg:ml-64" : "lg:ml-20",
          // Add top padding on mobile for menu button
          "pt-16 lg:pt-0"
        )}>
          <ClientHeader />
          <div className="flex-1 overflow-y-auto">
            {/* Content area - matches admin layout */}
            <div className="p-6 lg:p-8 w-full">
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarContext.Provider>
  )
}

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <ClientAppLayout>
        {children}
      </ClientAppLayout>
      <Toaster position="bottom-right" />
    </ThemeProvider>
  )
}
