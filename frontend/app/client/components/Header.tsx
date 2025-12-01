
'use client'

import { Menu, Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from './ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
  } from "./ui/dropdown-menu"

export function Header({ title }: { title: string }) {
    const { setTheme } = useTheme()
  return (
    <header className="flex items-center justify-between p-3 sm:p-4 lg:p-6 border-b border-border/50 bg-background/95 backdrop-blur-sm sticky top-0 z-30 safe-top">
      <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
        <Button variant="ghost" size="icon" className="lg:hidden flex-shrink-0">
          <Menu className="w-5 h-5 sm:w-6 sm:h-6" />
        </Button>
        <h1 className="text-lg sm:text-xl lg:text-2xl font-bold truncate">{title}</h1>
      </div>
      <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
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
      </div>
    </header>
  )
}
