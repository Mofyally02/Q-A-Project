'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'

type SidebarItem = {
  icon: React.ComponentType<{ className?: string }>
  label: string
  route: string
  badge?: number
}

type SidebarProps = {
  items: SidebarItem[]
  title: string
  className?: string
}

export default function Sidebar({ items, title, className }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col border-r bg-white/90 backdrop-blur sticky top-0 h-screen transition-all duration-300',
        collapsed ? 'w-20' : 'w-64',
        className
      )}
    >
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <h2 className="text-lg font-bold text-slate-900">{title}</h2>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-2 rounded-lg hover:bg-slate-100 transition"
          >
            <svg
              className="w-5 h-5 text-slate-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={collapsed ? 'M9 5l7 7-7 7' : 'M15 19l-7-7 7-7'}
              />
            </svg>
          </button>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.route || pathname.startsWith(item.route + '/')
          
          return (
            <button
              key={item.route}
              onClick={() => router.push(item.route)}
              className={cn(
                'flex items-center w-full gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition',
                'hover:bg-slate-100',
                isActive
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-slate-600',
                collapsed && 'justify-center'
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.badge && item.badge > 0 && (
                    <span className="px-2 py-0.5 text-xs bg-blue-600 text-white rounded-full">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </button>
          )
        })}
      </nav>
    </aside>
  )
}

