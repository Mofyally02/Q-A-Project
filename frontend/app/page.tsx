'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'

export default function Home() {
  const router = useRouter()
  // Use safe selectors to prevent undefined access
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)
  const userRole = useAuthStore((state) => state.user?.role ?? null) // Safe access with fallback
  const isHydrated = useAuthStore((state) => state.isHydrated)

  useEffect(() => {
    // Wait for auth store to hydrate before redirecting
    if (!isHydrated) return
    
    // Check authentication status
    if (isAuthenticated) {
      if (!userRole) {
        router.push('/auth') // Fallback if userRole is null
        return
      }
      // Redirect based on role
      // Super admin always defaults to admin dashboard, but can access all routes
      // Convert to string for comparison to handle both enum and string values
      const roleString: string = typeof userRole === 'string' ? userRole : String(userRole)
      
      // Check super admin first (by email or role)
      if (user?.email === 'allansaiti02@gmail.com' || 
          roleString === UserRole.SUPER_ADMIN || 
          roleString === 'super_admin') {
        router.push('/admin/dashboard') // Super admin defaults to admin dashboard
      } else if (roleString === UserRole.ADMIN || 
                 roleString === UserRole.ADMIN_EDITOR || 
                 roleString === 'admin' || 
                 roleString === 'admin_editor') {
        router.push('/admin/dashboard')
      } else if (roleString === UserRole.EXPERT || roleString === 'expert') {
        router.push('/expert/tasks') // Redirect to expert tasks page
      } else if (roleString === UserRole.CLIENT || roleString === 'client') {
        router.push('/client/dashboard') // Redirect to client dashboard page
      } else {
        router.push('/auth') // Fallback, maybe to a generic dashboard or login
      }
    } else {
      router.push('/auth') // Redirect to auth page if not authenticated
    }
  }, [isAuthenticated, userRole, isHydrated, router])

  // Optionally, render a loading spinner or null while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="flex flex-col items-center space-y-4 animate-fade-in">
          <div className="spinner w-10 h-10 sm:w-12 sm:h-12"></div>
          <p className="text-gray-600 dark:text-gray-400 font-medium text-sm sm:text-base">Loading...</p>
        </div>
      </div>
  )
}

