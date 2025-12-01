'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { FolderKanban, Loader2, Search, Filter, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function AdminTasksPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [tasks, setTasks] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!user) return
    const isAdmin = user.role === UserRole.ADMIN || 
                   user.role === UserRole.SUPER_ADMIN || 
                   user.role === UserRole.ADMIN_EDITOR ||
                   user.email === 'allansaiti02@gmail.com'
    if (!isAdmin) {
      toast.error('Admin access only')
      router.replace('/admin/dashboard')
      return
    }
    loadTasks()
  }, [user, router])

  const loadTasks = async () => {
    try {
      setLoading(true)
      // Use questions endpoint for tasks (pending/processing questions)
      const response = await apiHelpers.getQuestions({
        status: 'processing,submitted,review'
      })
      if (response.data?.success) {
        setTasks(response.data.data?.questions || [])
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = !searchQuery || 
      task.question_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.subject?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || task.status === filterStatus
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading tasks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Tasks</h1>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">All Status</option>
            <option value="submitted">Submitted</option>
            <option value="processing">Processing</option>
            <option value="review">Review</option>
          </select>
        </div>
      </Card>

      {/* Tasks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => (
            <Card key={task.question_id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      {task.subject || `Task #${task.question_id?.slice(0, 8)}`}
                    </h3>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        task.status === 'processing' ? 'bg-yellow-500/10 text-yellow-500' :
                        task.status === 'review' ? 'bg-blue-500/10 text-blue-500' :
                        'bg-gray-500/10 text-gray-500'
                      }`}
                    >
                      {task.status || 'Unknown'}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>ID: #{task.question_id?.slice(0, 8)}</p>
                  <p>Created: {new Date(task.created_at).toLocaleDateString()}</p>
                </div>
                <div className="pt-4 border-t border-border">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => router.push(`/admin/questions/${task.question_id}`)}
                  >
                    <FolderKanban className="w-4 h-4 mr-2" />
                    Manage Task
                  </Button>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <FolderKanban className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No tasks found</p>
          </div>
        )}
      </div>
    </div>
  )
}

