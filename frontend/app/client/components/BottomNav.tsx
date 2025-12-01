
'use client'

import { Home, Plus, Clock, MessageSquare } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '../lib/utils'

const clientNavItems = [
  { icon: Home, label: 'Home', route: '/client/dashboard' },
  { icon: Plus, label: 'Ask', route: '/client/ask' },
  { icon: Clock, label: 'History', route: '/client/history' },
  { icon: MessageSquare, label: 'Chat', route: '/client/chat' },
]

const expertNavItems = [
    { icon: Home, label: 'Tasks', route: '/expert/tasks' },
    { icon: Clock, label: 'Completed', route: '/expert/completed' },
    { icon: MessageSquare, label: 'Chat', route: '/expert/chat' },
    { icon: Plus, label: 'Profile', route: '/expert/settings' },
]

export function BottomNav({ role }: { role: 'client' | 'expert' }) {
  const pathname = usePathname()
  const items = role === 'client' ? clientNavItems : expertNavItems

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 h-20 sm:h-16 glass border-t border-border/50 z-50 safe-bottom shadow-lg">
      <nav className="flex items-center justify-around h-full px-2">
        {items.map(({ icon: Icon, label, route }) => (
          <Link
            key={label}
            href={route}
            className={cn(
              'flex flex-col items-center justify-center text-xs sm:text-sm gap-1 transition-all duration-200 w-full h-full rounded-lg active:scale-95',
              pathname === route
                ? 'text-primary'
                : 'text-foreground/60 hover:text-primary'
            )}
          >
            <div className={cn(
              'p-2 sm:p-2.5 rounded-full transition-all duration-200 relative',
              pathname === route 
                ? 'bg-primary/10 scale-110' 
                : 'hover:bg-foreground/5'
            )}>
              <Icon className={cn(
                "w-5 h-5 sm:w-6 sm:h-6",
                pathname === route && "scale-110"
              )} />
              {pathname === route && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full animate-pulse" />
              )}
            </div>
            <span className="font-medium">{label}</span>
          </Link>
        ))}
      </nav>
    </div>
  )
}
