
'use client'

import { Clock, Loader2, Briefcase, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function ExpertPendingReviewsPage() {
  const router = useRouter()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [pendingReviews, setPendingReviews] = useState<any>(null) // Replace with actual type

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getPendingReviews: async () => {
      // Simulate API call
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                pending_count: 5,
                assigned_count: 2,
                total_pending: 7
              }
            }
          })
        }, 800)
      })
    }
  }

  useEffect(() => {
    // if (!user || user.role !== UserRole.EXPERT) {
    //   router.push('/login')
    //   toast.error('Expert access only.')
    //   return
    // }

    const fetchPendingReviews = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getPendingReviews() // Assuming a getPendingReviews API
        if (response.data.success) {
          setPendingReviews(response.data.data)
        } else {
          toast.error(response.data.message || 'Failed to load pending reviews.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching pending reviews.')
      } finally {
        setLoading(false)
      }
    }
    fetchPendingReviews()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const { pending_count = 0, assigned_count = 0, total_pending = 0 } = pendingReviews || {}

  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft flex items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg">
          <Clock className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Pending Reviews</h1>
          <p className="text-muted-foreground mt-1">Overview of your pending and assigned review tasks</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Briefcase className="w-8 h-8 text-blue-500" />
          <div>
            <p className="text-muted-foreground text-sm">New Reviews Available</p>
            <p className="text-foreground text-2xl font-semibold">{pending_count}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <CheckCircle className="w-8 h-8 text-green-500" />
          <div>
            <p className="text-muted-foreground text-sm">Assigned for Review</p>
            <p className="text-foreground text-2xl font-semibold">{assigned_count}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Clock className="w-8 h-8 text-yellow-500" />
          <div>
            <p className="text-muted-foreground text-sm">Total Pending</p>
            <p className="text-foreground text-2xl font-semibold">{total_pending}</p>
          </div>
        </div>
      </div>

      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft">
        <h2 className="text-xl font-bold text-foreground mb-4">Review Queue Status</h2>
        <p className="text-muted-foreground">
          This page would typically show a detailed list of questions in the pending review queue.
          For now, it provides a summary of available tasks. Navigate to 'My Tasks' to pick up new assignments.
        </p>
        <div className="mt-6">
          <Link href="/expert/tasks" passHref>
            <Button>
              Go to My Tasks
            </Button>
          </Link>
        </div>
      </div>
      </div>
    </div>
  )
}
