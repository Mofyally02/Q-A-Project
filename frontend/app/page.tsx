'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, userRole } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check authentication status
    if (isAuthenticated) {
      // Redirect based on role
      if (userRole === 'admin') {
        router.push('/admin/dashboard')
      } else if (userRole === 'expert') {
        router.push('/expert/reviews')
      } else {
        router.push('/dashboard')
      }
    } else {
      router.push('/auth')
    }
    setIsLoading(false)
  }, [isAuthenticated, userRole, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center space-y-4">
          <div className="spinner w-8 h-8"></div>
          <p className="text-gray-600 font-medium">Loading AL-Tech Academy Q&A...</p>
        </div>
      </div>
    )
  }

  return null
}

