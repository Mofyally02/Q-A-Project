
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function ClientRootPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to the client dashboard by default
    router.replace('/client/dashboard')
  }, [router])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <p className="text-foreground">Loading Client UI...</p>
    </div>
  )
}
