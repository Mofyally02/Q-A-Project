'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Moon, Sun, Bell, Search, Settings, User, GraduationCap, Shield } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/app/client/lib/utils'

const SUPER_ADMIN_EMAIL = 'allansaiti02@gmail.com'

const routes = [
  { 
    value: 'client', 
    label: 'Client Dashboard', 
    icon: User, 
    path: '/client/dashboard',
  },
  { 
    value: 'expert', 
    label: 'Expert Dashboard', 
    icon: GraduationCap, 
    path: '/expert/tasks',
  },
  { 
    value: 'admin', 
    label: 'Admin Dashboard', 
    icon: Shield, 
    path: '/admin/dashboard',
  },
]

export function AdminHeader() {
  const { setTheme, theme } = useTheme()
  const { user, userInitials } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const [settingsOpen, setSettingsOpen] = useState(false)

  const isSuperAdmin = user?.email === SUPER_ADMIN_EMAIL

  const handleRouteChange = (path: string) => {
    setSettingsOpen(false)
    router.push(path)
  }

  const getCurrentRoute = () => {
    if (pathname?.startsWith('/admin')) return 'admin'
    if (pathname?.startsWith('/expert')) return 'expert'
    if (pathname?.startsWith('/client')) return 'client'
    return 'admin'
  }

  const currentRoute = getCurrentRoute()

  return (
    <header className={cn(
      "flex items-center justify-between w-full",
      "pl-[10px] pr-[10px] sm:px-4 md:px-6 lg:px-8 xl:px-10",
      "py-3 sm:py-4",
      "border-b border-border/50 glass",
      "sticky top-0 z-50 safe-top shadow-sm",
      "bg-background/95 backdrop-blur-md"
    )}>
      {/* Left: Title */}
      <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
        <h1 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-foreground truncate">
          AL-Tech Q&A's
        </h1>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
        {/* Search */}
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-9 w-9 sm:h-10 sm:w-10 text-foreground hover:text-primary hover:bg-accent/50 border border-transparent hover:border-border/50"
          title="Search"
        >
          <Search className="w-5 h-5" />
        </Button>

        {/* Notifications */}
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-9 w-9 sm:h-10 sm:w-10 relative text-foreground hover:text-primary hover:bg-accent/50 border border-transparent hover:border-border/50"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-destructive rounded-full border-2 border-background"></span>
        </Button>

        {/* Settings Dropdown with Route Switching */}
        <DropdownMenu open={settingsOpen} onOpenChange={setSettingsOpen}>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="outline" 
              size="icon" 
              className="h-9 w-9 sm:h-10 sm:w-10 border-border/50 hover:border-primary hover:bg-accent/50"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
              <span className="sr-only">Settings</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            {/* Route Switching (Super Admin Only) */}
            {isSuperAdmin && (
              <>
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase">
                  Switch Route
                </div>
                {routes.map((route) => {
                  const Icon = route.icon
                  const isActive = currentRoute === route.value
                  
                  return (
                    <DropdownMenuItem
                      key={route.value}
                      onClick={() => handleRouteChange(route.path)}
                      className={cn(
                        "cursor-pointer flex items-center gap-2",
                        isActive && "bg-primary/10 text-primary"
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{route.label}</span>
                      {isActive && (
                        <span className="ml-auto text-xs text-primary">●</span>
                      )}
                    </DropdownMenuItem>
                  )
                })}
                <DropdownMenuSeparator />
              </>
            )}

            {/* Theme Toggle */}
            <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase">
              Theme
            </div>
            <DropdownMenuItem 
              onClick={() => setTheme("light")} 
              className="cursor-pointer"
            >
              <Sun className="w-4 h-4 mr-2" />
              Light
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => setTheme("dark")} 
              className="cursor-pointer"
            >
              <Moon className="w-4 h-4 mr-2" />
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => setTheme("system")} 
              className="cursor-pointer"
            >
              <Settings className="w-4 h-4 mr-2" />
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Avatar */}
        <div className="ml-1 sm:ml-2">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-semibold text-sm shadow-md border-2 border-background hover:scale-105 transition-transform cursor-pointer">
            {userInitials}
          </div>
        </div>
      </div>
    </header>
  )
}
