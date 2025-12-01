'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { Button } from '@/app/client/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Shield, User, GraduationCap, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const SUPER_ADMIN_EMAIL = 'allansaiti02@gmail.com'

const roles = [
  { 
    value: 'client', 
    label: 'Client', 
    icon: User, 
    route: '/client/dashboard',
    description: 'Access client features and ask questions'
  },
  { 
    value: 'expert', 
    label: 'Expert', 
    icon: GraduationCap, 
    route: '/expert/tasks',
    description: 'Review and answer questions'
  },
  { 
    value: 'admin', 
    label: 'Admin', 
    icon: Shield, 
    route: '/admin/dashboard',
    description: 'Manage platform and users'
  },
]

export function RoleSwitcher() {
  const { user } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<string | null>(null)

  // Only show for super admin
  if (!user || user.email !== SUPER_ADMIN_EMAIL) {
    return null
  }

  const handleRoleSwitch = (role: string, route: string) => {
    setSelectedRole(role)
    setIsOpen(false)
    router.push(route)
  }

  const getCurrentRole = () => {
    if (pathname?.startsWith('/admin')) return 'admin'
    if (pathname?.startsWith('/expert')) return 'expert'
    if (pathname?.startsWith('/client')) return 'client'
    return 'client'
  }

  const currentRole = getCurrentRole()

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="hidden md:flex items-center gap-2"
      >
        <Settings className="w-4 h-4" />
        <span className="capitalize">{currentRole}</span>
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Switch Role</DialogTitle>
            <DialogDescription>
              As super admin, you can access all routes. Select a role to switch views.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-3 py-4">
            {roles.map((role) => {
              const Icon = role.icon
              const isActive = currentRole === role.value
              
              return (
                <button
                  key={role.value}
                  onClick={() => handleRoleSwitch(role.value, role.route)}
                  className={cn(
                    "flex items-start gap-4 p-4 rounded-lg border-2 transition-all text-left",
                    "hover:bg-accent hover:border-primary",
                    isActive 
                      ? "border-primary bg-primary/5" 
                      : "border-border"
                  )}
                >
                  <div className={cn(
                    "p-2 rounded-lg",
                    isActive ? "bg-primary text-primary-foreground" : "bg-muted"
                  )}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold capitalize">{role.label}</span>
                      {isActive && (
                        <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{role.description}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

