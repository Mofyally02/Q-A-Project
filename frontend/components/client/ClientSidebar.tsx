'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Plus,
  Clock,
  MessageSquare,
  Wallet,
  Bell,
  Settings,
  Menu,
  X,
  LogOut
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'next/navigation'

const clientSidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', route: '/client/dashboard' },
  { icon: Plus, label: 'Ask Question', route: '/client/ask' },
  { icon: Clock, label: 'My Questions', route: '/client/history' },
  { icon: MessageSquare, label: 'Live Answers', route: '/client/chat' },
  { icon: Wallet, label: 'Credits & Billing', route: '/client/wallet' },
  { icon: Bell, label: 'Notifications', route: '/client/notifications' },
  { icon: Settings, label: 'Settings', route: '/client/settings' },
]

export function ClientSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { logout } = useAuthStore()
  const [isExpanded, setIsExpanded] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/auth')
  }

  const handleLinkClick = () => {
    // Safe check for window width (client-side only)
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      setIsMobileOpen(false)
    }
  }

  const SidebarContent = () => (
    <>
      {/* Logo Section */}
      <div className={cn(
        "flex items-center mb-8 transition-all duration-300",
        isExpanded ? "justify-start px-4" : "justify-center"
      )}>
        {isExpanded ? (
          <Link href="/client/dashboard" className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-xl shadow-md">
              A
            </div>
            <span className="text-foreground font-semibold text-lg">AI-TECH</span>
          </Link>
        ) : (
          <Link href="/client/dashboard" className="flex items-center justify-center">
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg shadow-md">
              A
            </div>
          </Link>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1">
        {clientSidebarItems.map(({ icon: Icon, label, route }) => {
          const isActive = pathname === route || (route !== '/client/dashboard' && pathname.startsWith(route))
          return (
            <Link
              key={route}
              href={route}
              onClick={handleLinkClick}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group relative",
                isActive
                  ? "bg-primary/20 text-primary"
                  : "text-foreground/70 hover:bg-accent/50 hover:text-foreground",
                isExpanded ? "justify-start" : "justify-center"
              )}
              title={!isExpanded ? label : undefined}
            >
              <Icon 
                size={20} 
                className={cn(
                  "flex-shrink-0",
                  isActive && "text-primary"
                )} 
              />
              {isExpanded && (
                <span className="text-sm font-medium whitespace-nowrap">
                  {label}
                </span>
              )}
              {/* Tooltip for collapsed state */}
              {!isExpanded && (
                <div className="absolute left-full ml-3 px-3 py-1.5 bg-popover text-popover-foreground text-xs font-medium rounded-md opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-200 whitespace-nowrap z-50 shadow-xl border border-border">
                  {label}
                  <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-popover"></div>
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Live Chat Section - Animated with Ticket System */}
      <div className={cn(
        "mt-auto pt-4 border-t border-border/50",
        isExpanded ? "px-4" : "px-2"
      )}>
        <Link
          href="/client/tickets"
          onClick={handleLinkClick}
          className={cn(
            "flex items-center gap-3 px-4 py-3 rounded-lg bg-primary/10 text-primary mb-4 transition-all duration-200 group relative",
            "cursor-pointer z-10 active:scale-95",
            isExpanded ? "justify-start" : "justify-center",
            "hover:bg-primary/20",
            "ring-2 ring-primary/30 hover:ring-primary/50",
            "shadow-lg hover:shadow-xl",
            "animate-pulse group-hover:animate-none"
          )}
          title={!isExpanded ? "Create Ticket to Chat with Admin" : undefined}
        >
          <div className="relative flex-shrink-0 pointer-events-none">
            <MessageSquare size={20} className="flex-shrink-0 animate-bounce-slow" />
            {/* Animated notification dot */}
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-background animate-ping pointer-events-none"></span>
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-background pointer-events-none"></span>
          </div>
          {isExpanded && (
            <div className="flex-1">
              <span className="text-sm font-medium block">Live Chat</span>
              <span className="text-xs text-primary/70">Create a ticket</span>
            </div>
          )}
          {/* Tooltip for collapsed state */}
          {!isExpanded && (
            <div className="absolute left-full ml-3 px-3 py-2 bg-popover text-popover-foreground text-xs font-medium rounded-md opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-200 whitespace-nowrap z-50 shadow-xl border border-border">
              <div className="font-semibold mb-1"> Live Chat</div>
              <div className="text-xs opacity-80">Create ticket to start</div>
              <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-popover"></div>
            </div>
          )}
        </Link>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className={cn(
            "flex items-center gap-3 px-4 py-3 rounded-lg text-destructive hover:bg-destructive/10 transition-all duration-200 w-full",
            isExpanded ? "justify-start" : "justify-center"
          )}
          title={!isExpanded ? "Logout" : undefined}
        >
          <LogOut size={20} className="flex-shrink-0" />
          {isExpanded && (
            <span className="text-sm font-medium">Logout</span>
          )}
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 bg-primary text-primary-foreground rounded-lg p-2.5 shadow-lg hover:bg-primary/90 active:scale-95 transition-all duration-200"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="lg:hidden fixed inset-0 bg-background/80 backdrop-blur-sm z-40 transition-opacity duration-300"
          aria-hidden="true"
        />
      )}

      {/* Desktop Sidebar */}
      <aside
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
        className={cn(
          "hidden lg:flex lg:flex-col fixed left-0 top-0 h-screen z-30",
          "bg-background border-r border-border/50",
          "transition-all duration-300 ease-in-out",
          isExpanded ? "w-64" : "w-20",
          isExpanded ? "p-6" : "p-4"
        )}
        data-expanded={isExpanded}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            "absolute -right-3 top-1/2 -translate-y-1/2 z-50",
            "bg-primary text-primary-foreground rounded-full shadow-lg",
            "hover:shadow-xl hover:scale-110 active:scale-95",
            "transition-all duration-200",
            "flex items-center justify-center w-8 h-8"
          )}
          aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
        >
          {isExpanded ? (
            <X size={16} className="rotate-45" />
          ) : (
            <Menu size={16} />
          )}
        </button>

        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          "lg:hidden fixed top-0 left-0 h-full z-50",
          "bg-background border-r border-border/50",
          "shadow-2xl transition-transform duration-300 ease-in-out",
          "flex flex-col w-64 p-6",
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <SidebarContent />
      </aside>
    </>
  )
}

