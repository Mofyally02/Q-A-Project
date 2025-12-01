'use client'

import { cn } from '../lib/utils'
import { Home, Plus, Clock, MessageSquare, TrendingUp, Star, Bell, Settings, LogOut, ChevronLeft, ChevronRight, Users, KeySquare, BarChart3, ShieldCheck, Menu, X } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import React, { createContext, useState, useContext, useEffect, useRef } from 'react'

interface SidebarContextType {
    isCollapsed: boolean;
    isHovered: boolean;
    isMobileOpen: boolean;
    toggleSidebar: () => void;
    toggleMobile: () => void;
    setIsHovered: (value: boolean) => void;
}

const SidebarContext = createContext<SidebarContextType>({
    isCollapsed: false,
    isHovered: false,
    isMobileOpen: false,
    toggleSidebar: () => {},
    toggleMobile: () => {},
    setIsHovered: () => {},
});

export const useSidebar = () => useContext(SidebarContext);

interface SidebarProviderProps {
    children: React.ReactNode;
}

export const SidebarProvider = ({ children }: SidebarProviderProps) => {
    const [isCollapsed, setIsCollapsed] = useState(true);
    const [isHovered, setIsHovered] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    
    const toggleSidebar = () => setIsCollapsed(!isCollapsed);
    const toggleMobile = () => setIsMobileOpen(!isMobileOpen);

    // Close mobile menu on route change
    useEffect(() => {
        setIsMobileOpen(false);
    }, []);

    return (
        <SidebarContext.Provider value={{ 
            isCollapsed, 
            isHovered, 
            isMobileOpen,
            toggleSidebar, 
            toggleMobile,
            setIsHovered 
        }}>
            {children}
        </SidebarContext.Provider>
    );
};

const clientSidebarItems = [
  { icon: Home, label: 'Dashboard', route: '/client/dashboard' },
  { icon: Plus, label: 'Ask Question', route: '/client/ask' },
  { icon: Clock, label: 'My Questions', route: '/client/history' },
  { icon: MessageSquare, label: 'Live Answers', route: '/client/chat' },
  { icon: TrendingUp, label: 'Credits & Billing', route: '/client/wallet' },
  { icon: Bell, label: 'Notifications', route: '/client/notifications' },
  { icon: Settings, label: 'Settings', route: '/client/settings' },
]

const expertSidebarItems = [
    { icon: Home, label: 'My Tasks', route: '/expert/tasks' },
    { icon: Clock, label: 'Completed', route: '/expert/completed' },
    { icon: TrendingUp, label: 'Earnings', route: '/expert/earnings' },
    { icon: MessageSquare, label: 'Chat with Clients', route: '/expert/chat' },
    { icon: Star, label: 'My Ratings', route: '/expert/ratings' },
    { icon: Bell, label: 'Notifications', route: '/expert/notifications' },
    { icon: Settings, label: 'Settings', route: '/expert/settings' },
]

const adminSidebarItems = [
  { icon: Home, label: 'Dashboard', route: '/admin/dashboard' },
  { icon: Users, label: 'Users', route: '/admin/users' },
  { icon: KeySquare, label: 'API Keys', route: '/admin/api-keys' },
  { icon: Settings, label: 'Settings', route: '/admin/controls' },
  { icon: BarChart3, label: 'Analytics', route: '/admin/analytics' },
  { icon: ShieldCheck, label: 'Compliance', route: '/admin/compliance' },
  { icon: Bell, label: 'Notifications', route: '/admin/notifications' },
]

export function GlassSidebar({ role }: { role: 'client' | 'expert' | 'admin' }) {
  const pathname = usePathname()
  const router = useRouter()
  const { logout } = useAuthStore()
  const items = role === 'client' ? clientSidebarItems : role === 'expert' ? expertSidebarItems : adminSidebarItems
  const { isCollapsed, isHovered, isMobileOpen, toggleSidebar, toggleMobile, setIsHovered } = useSidebar();
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sidebarRef = useRef<HTMLElement>(null);

  // Close mobile menu on route change
  useEffect(() => {
    if (isMobileOpen) {
      toggleMobile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  // Automatic expand on hover (only if collapsed, desktop only)
  const handleMouseEnter = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = null;
    }
    if (isCollapsed && window.innerWidth >= 1024) {
      setIsHovered(true);
    }
  };

  // Automatic collapse on leave (only if it was auto-expanded via hover)
  const handleMouseLeave = () => {
    if (isCollapsed && isHovered && window.innerWidth >= 1024) {
      hoverTimeoutRef.current = setTimeout(() => {
        setIsHovered(false);
      }, 200);
    }
  };

  // Determine if sidebar should appear expanded
  const shouldShowExpanded = !isCollapsed || (isCollapsed && isHovered);

  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, [isCollapsed, isHovered]);

  const handleLogout = () => {
    logout()
    router.push('/auth')
  }

  const handleLinkClick = () => {
    if (window.innerWidth < 1024) {
      toggleMobile();
    }
  }

  // Mobile Menu Button
  const MobileMenuButton = () => (
    <button
      onClick={toggleMobile}
      className={cn(
        "lg:hidden fixed top-4 left-4 z-50",
        "bg-primary text-primary-foreground rounded-lg p-2.5 shadow-lg",
        "hover:bg-primary/90 active:scale-95",
        "transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
      )}
      aria-label="Toggle menu"
    >
      {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
    </button>
  );

  // Mobile Overlay
  const MobileOverlay = () => (
    isMobileOpen && (
      <div
        onClick={toggleMobile}
        className={cn(
          "lg:hidden fixed inset-0 bg-background/80 backdrop-blur-sm z-40",
          "transition-opacity duration-300",
          isMobileOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        aria-hidden="true"
      />
    )
  );

  // Sidebar Content
  const SidebarContent = () => (
    <>
      {/* Menu Title */}
      <div className={cn(
        "flex items-center mb-6 transition-all duration-300 overflow-hidden",
        shouldShowExpanded ? "justify-start" : "justify-center"
      )}>
        <p className={cn(
          "font-bold text-foreground uppercase tracking-wider transition-all duration-300 whitespace-nowrap",
          shouldShowExpanded ? "opacity-100 text-sm" : "opacity-0 w-0 text-xs"
        )}>
          {role === 'client' ? 'CLIENT MENU' : role === 'expert' ? 'EXPERT MENU' : 'ADMIN MENU'}
        </p>
      </div>

      {/* Toggle Button (Desktop only) */}
      <button 
        onClick={toggleSidebar} 
        className={cn(
          "hidden lg:flex absolute top-1/2 -right-3 z-50",
          "bg-primary text-primary-foreground rounded-full shadow-lg",
          "hover:shadow-xl hover:scale-110 active:scale-95",
          "transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          "items-center justify-center",
          "w-8 h-8"
        )}
        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {isCollapsed ? (
          <ChevronRight size={16} />
        ) : (
          <ChevronLeft size={16} />
        )}
      </button>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1.5 overflow-y-auto overflow-x-hidden">
        {items.map(({ icon: Icon, label, route }) => (
          <Link
            key={label}
            href={route}
            onClick={handleLinkClick}
            className={cn(
              'flex items-center w-full gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
              'active:scale-95 relative group/item',
              pathname === route
                ? 'bg-primary/10 text-primary shadow-sm border border-primary/20 font-semibold'
                : 'text-foreground/70 hover:bg-accent/50 hover:text-accent-foreground',
              shouldShowExpanded ? "justify-start" : "justify-center px-2"
            )}
            title={shouldShowExpanded ? undefined : label}
          >
            <Icon 
              size={20} 
              className="flex-shrink-0" 
            />
            <span className={cn(
              "truncate transition-all duration-300 whitespace-nowrap",
              shouldShowExpanded ? "opacity-100 max-w-full" : "opacity-0 max-w-0 overflow-hidden"
            )}>
              {label}
            </span>
            {/* Tooltip for collapsed state (Desktop only) */}
            {!shouldShowExpanded && (
              <div className="hidden lg:block absolute left-full ml-3 px-3 py-1.5 bg-popover text-popover-foreground text-xs font-medium rounded-md opacity-0 group-hover/item:opacity-100 pointer-events-none transition-all duration-200 whitespace-nowrap z-50 shadow-xl border border-border">
                {label}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-popover"></div>
              </div>
            )}
          </Link>
        ))}
      </nav>

      {/* Logout Button */}
      <div className="mt-auto pt-4 border-t border-border/50">
        <button
          onClick={handleLogout}
          className={cn(
            "flex items-center w-full gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-destructive hover:bg-destructive/10 transition-all duration-200 active:scale-95 relative group/item",
            shouldShowExpanded ? "justify-start" : "justify-center px-2"
          )}
          title={shouldShowExpanded ? undefined : "Logout"}
        >
          <LogOut size={20} className="flex-shrink-0" />
          <span className={cn(
            "truncate transition-all duration-300 whitespace-nowrap",
            shouldShowExpanded ? "opacity-100 max-w-full" : "opacity-0 max-w-0 overflow-hidden"
          )}>
            Logout
          </span>
          {/* Tooltip for collapsed state (Desktop only) */}
          {!shouldShowExpanded && (
            <div className="hidden lg:block absolute left-full ml-3 px-3 py-1.5 bg-popover text-popover-foreground text-xs font-medium rounded-md opacity-0 group-hover/item:opacity-100 pointer-events-none transition-all duration-200 whitespace-nowrap z-50 shadow-xl border border-border">
              Logout
              <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-popover"></div>
            </div>
          )}
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <MobileMenuButton />

      {/* Mobile Overlay */}
      <MobileOverlay />

      {/* Desktop Sidebar */}
      <aside 
        ref={sidebarRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className={cn(
          "hidden lg:flex lg:flex-col border-r border-border/50 glass sticky top-0 h-screen z-40",
          "shadow-lg backdrop-blur-md bg-background/95",
          "transition-all duration-300 ease-in-out",
          shouldShowExpanded ? "w-64" : "w-20",
          shouldShowExpanded ? "p-6" : "p-4"
        )}
      >
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          "lg:hidden fixed top-0 left-0 h-full z-50",
          "bg-background/98 backdrop-blur-xl border-r border-border/50",
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
