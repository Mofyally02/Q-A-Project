'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function ExpertRootPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to the expert tasks page by default
    router.replace('/expert/tasks')
  }, [router])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <p className="text-foreground">Loading Expert UI...</p>
    </div>
  )
}