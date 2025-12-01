'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Briefcase, CheckCircle, Clock, TrendingUp, MessageSquare, Star, Bell, Settings, Loader2, Eye, ThumbsUp, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'
import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'


export default function ExpertTasksPage() {
  const router = useRouter()
//   const { user } = useAuthStore() // Assuming auth store is available
  const [loading, setLoading] = useState(true)
  const [tasks, setTasks] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [statusFilter, setStatusFilter] = useState('')

  // Mock user
  const user = { role: 'expert' }


//   useEffect(() => {
//     hydrateApiAuth()
//   }, [])

  useEffect(() => {
    if (!user) return
    // if (user.role !== UserRole.EXPERT) {
    //   toast.error('Expert access only')
    //   router.replace('/dashboard')
    //   return
    // }
    loadTasks()
  }, [user, router, statusFilter])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const response: any = await apiHelpers.getExpertTasks({
        status: statusFilter || undefined
      })
      setTasks(response.data?.data?.tasks ?? [])
      setTotal(response.data?.data?.total ?? 0)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (answerId: string) => {
    try {
      await apiHelpers.submitReview({
        answer_id: answerId,
        is_approved: true,
        notes: 'Approved by expert'
      })
      toast.success('Answer approved successfully')
      loadTasks()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to approve')
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">My Tasks</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">Review and approve AI-generated answers</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 sm:px-4 py-2 text-sm sm:text-base border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary w-full sm:w-auto"
        >
          <option value="">All Status</option>
          <option value="review">Review</option>
          <option value="in_review">In Review</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <div
              key={task.question_id}
              className="glass bg-card/60 rounded-lg border shadow-soft p-6 space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground">{task.subject}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    Client: {task.client_email}
                  </p>
                </div>
                <span className={cn("px-2 py-1 rounded-full text-xs font-medium",
                  task.priority === 'urgent' 
                    ? 'bg-destructive/20 text-destructive'
                    : 'bg-primary/20 text-primary'
                )}>
                  {task.priority || 'normal'}
                </span>
              </div>

              <div className="space-y-2 text-sm text-foreground/80">
                <p className="line-clamp-2">
                  {task.content?.data || 'No content'}
                </p>
                {task.humanized_response && (
                  <div className="p-3 bg-background/50 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">AI Answer:</p>
                    <p className="text-sm line-clamp-3">
                      {task.humanized_response}
                    </p>
                  </div>
                )}
                {task.ai_content_percentage && (
                  <p className="text-xs text-muted-foreground">
                    AI Content: {task.ai_content_percentage}% | 
                    Uniqueness: {(task.uniqueness_score * 100).toFixed(0)}%
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2 pt-4 border-t border-border">
                <Link
                  href={`/expert/reviews/${task.answer_id}`} // This page needs to be created
                  passHref
                >
                  <Button variant="outline" className="flex-1 flex items-center justify-center gap-2">
                    <Eye className="w-4 h-4" />
                    Review
                  </Button>
                </Link>
                {task.answer_id && (
                  <Button
                    onClick={() => handleApprove(task.answer_id)}
                    className="px-4 py-2 flex items-center gap-2"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
          {tasks.length === 0 && (
            <div className="col-span-full text-center py-12 text-muted-foreground">
              <Briefcase className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
              <p>No tasks available</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}