
'use client'

import { CheckCircle, Loader2, Briefcase } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function ExpertCompletedTasksPage() {
  const router = useRouter()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [completedTasks, setCompletedTasks] = useState<any[]>([]) // Replace with actual type
  const [total, setTotal] = useState(0)
  const [skip, setSkip] = useState(0)

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getCompletedTasks: async ({ skip, limit }: { skip: number, limit: number }) => {
      // Simulate API call
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                tasks: [
                  { question_id: 'qc1', subject: 'Algebra Review', client_email: 'client1@example.com', status: 'delivered', review_created_at: new Date().toISOString(), is_approved: true, overall_score: 4.5 },
                  { question_id: 'qc2', subject: 'Poetry Analysis', client_email: 'client2@example.com', status: 'delivered', review_created_at: new Date().toISOString(), is_approved: true, overall_score: 5 },
                ].slice(skip, skip + limit),
                total: 2,
                skip: skip,
                limit: limit
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

    const fetchCompletedTasks = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getCompletedTasks({ skip, limit: 10 }) // Assuming a getCompletedTasks API
        if (response.data.success) {
          setCompletedTasks(response.data.data.tasks)
          setTotal(response.data.data.total)
        } else {
          toast.error(response.data.message || 'Failed to load completed tasks.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching completed tasks.')
      } finally {
        setLoading(false)
      }
    }
    fetchCompletedTasks()
  }, [skip])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg flex-shrink-0">
          <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">Completed Tasks</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">Answers you have reviewed and approved</p>
        </div>
      </div>

      <div className="glass bg-card/60 rounded-lg sm:rounded-lg border shadow-soft p-4 sm:p-6">
        {completedTasks.length > 0 ? (
          <div className="space-y-4">
            {completedTasks.map((task: any) => (
              <div
                key={task.question_id}
                className="flex items-center justify-between p-4 bg-background/50 rounded-lg shadow-sm"
              >
                <div>
                  <h3 className="font-semibold text-foreground">{task.subject}</h3>
                  <p className="text-muted-foreground text-sm">Client: {task.client_email}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Reviewed: {new Date(task.review_created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={cn("px-3 py-1 text-xs rounded-full",
                  task.is_approved ? 'bg-green-500/20 text-green-600' : 'bg-destructive/20 text-destructive'
                )}>
                  {task.is_approved ? 'Approved' : 'Rejected'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Briefcase className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
            <p>No completed tasks yet.</p>
          </div>
        )}

        <div className="flex items-center justify-between mt-6 pt-6 border-t border-border">
          <Button
            variant="outline"
            onClick={() => setSkip(Math.max(0, skip - 10))}
            disabled={skip === 0 || loading}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            onClick={() => setSkip(skip + 10)}
            disabled={skip + 10 >= total || loading}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
