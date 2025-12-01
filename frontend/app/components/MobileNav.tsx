'use client'

import { usePathname, useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

type MobileNavItem = {
  icon: React.ComponentType<{ className?: string }>
  label: string
  route: string
  badge?: number
}

type MobileNavProps = {
  items: MobileNavItem[]
}

export default function MobileNav({ items }: MobileNavProps) {
  const pathname = usePathname()
  const router = useRouter()

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-50">
      <div className="flex items-center justify-around px-2 py-2">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.route || pathname.startsWith(item.route + '/')
          
          return (
            <button
              key={item.route}
              onClick={() => router.push(item.route)}
              className={cn(
                'flex flex-col items-center gap-1 px-4 py-2 rounded-lg transition',
                isActive
                  ? 'text-blue-600'
                  : 'text-slate-500'
              )}
            >
              <div className="relative">
                <Icon className="w-6 h-6" />
                {item.badge && item.badge > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center">
                    {item.badge > 9 ? '9+' : item.badge}
                  </span>
                )}
              </div>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}

