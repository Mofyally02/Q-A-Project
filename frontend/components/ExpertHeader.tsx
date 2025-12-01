'use client'

import { Menu, Moon, Sun, Bell, Search } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/app/client/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/client/components/ui/dropdown-menu"
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/app/client/lib/utils'
import { RoleSwitcher } from './RoleSwitcher'

export function ExpertHeader() {
  const { setTheme } = useTheme()
  const { user, userInitials } = useAuthStore()

  return (
    <header className={cn(
      "flex items-center justify-between p-3 sm:p-4 lg:p-6",
      "border-b border-border/50 glass",
      "sticky top-0 z-30 safe-top shadow-sm"
    )}>
      <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
        <Button variant="ghost" size="icon" className="lg:hidden flex-shrink-0">
          <Menu className="w-5 h-5 sm:w-6 sm:h-6" />
        </Button>
        <h1 className="text-lg sm:text-xl lg:text-2xl font-bold truncate">Expert Portal</h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
        {/* Role Switcher (Super Admin Only) */}
        <RoleSwitcher />

        {/* Search */}
        <Button variant="ghost" size="icon" className="hidden sm:flex">
          <Search className="w-5 h-5" />
        </Button>

        {/* Theme Toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon" className="h-9 w-9 sm:h-10 sm:w-10">
              <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-32">
            <DropdownMenuItem onClick={() => setTheme("light")} className="cursor-pointer">
              Light
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")} className="cursor-pointer">
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")} className="cursor-pointer">
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-semibold text-sm">
          {userInitials}
        </div>
      </div>
    </header>
  )
}

