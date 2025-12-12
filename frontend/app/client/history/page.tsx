'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Home, Plus, Clock, MessageSquare, TrendingUp, Star, CheckCircle, Filter, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function ClientHistoryPage() {
  const router = useRouter()
  const { user, isAuthenticated, isHydrated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [questions, setQuestions] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    // Wait for auth store to hydrate from localStorage before checking auth
    if (!isHydrated) return
    
    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only')
      return
    }
    loadHistory()
  }, [user, isAuthenticated, isHydrated, router, page, statusFilter])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const response: any = await apiHelpers.getQuestionHistory({
        skip: (page - 1) * 20,
        limit: 20,
        status: statusFilter || undefined
      })
      const data = response.data?.data || response.data
      setQuestions(data?.questions ?? [])
      setTotal(data?.total ?? 0)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      submitted: 'bg-blue-500/20 text-blue-600',
      processing: 'bg-yellow-500/20 text-yellow-600',
      review: 'bg-amber-500/20 text-amber-600',
      delivered: 'bg-green-500/20 text-green-600',
      rated: 'bg-purple-500/20 text-purple-600'
    }
    return colors[status] || 'bg-gray-500/20 text-gray-600'
  }

  return (
    <div className="w-full space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">My Questions</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">View all your submitted questions and their status</p>
        </div>
        <Link href="/client/ask" passHref className="flex-shrink-0">
          <Button className="w-full sm:w-auto">
            <Plus className="w-4 h-4 mr-2" />
            Ask Question
          </Button>
        </Link>
      </div>

      <div className="glass bg-card/60 rounded-lg sm:rounded-lg border shadow-soft p-4 sm:p-6">
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <Filter className="w-5 h-5 text-foreground/70" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="px-4 py-2 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">All Status</option>
            <option value="submitted">Submitted</option>
            <option value="processing">Processing</option>
            <option value="review">Review</option>
            <option value="delivered">Delivered</option>
            <option value="rated">Rated</option>
          </select>
          <div className="flex-1" />
          <span className="text-sm text-muted-foreground">
            Showing {questions.length} of {total}
          </span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="space-y-4">
            {questions.map((question) => (
              <Link
                key={question.question_id}
                href={`/client/chat/${question.question_id}`}
                className="block glass bg-background/50 rounded-lg p-5 hover:bg-background/70 transition-colors shadow-soft"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-foreground">{question.subject}</h3>
                      <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(question.status))}>
                        {question.status}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-sm line-clamp-2 mb-3">
                      {question.content?.data || question.content || 'No preview available'}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{new Date(question.created_at).toLocaleString()}</span>
                      {question.humanized_response && (
                        <span className="text-green-600">✓ Answered</span>
                      )}
                      {question.overall_score && (
                        <span className="flex items-center gap-1 text-yellow-600">
                          <Star className="w-3 h-3 fill-yellow-500" />
                          {question.overall_score}
                        </span>
                      )}
                    </div>
                  </div>
                  <MessageSquare className="w-5 h-5 text-foreground/60 ml-4" />
                </div>
              </Link>
            ))}
            {questions.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
                <p>No questions found</p>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-between mt-6 pt-6 border-t border-border">
          <Button
            variant="outline"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1 || loading}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {Math.ceil(total / 20) || 1}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(page + 1)}
            disabled={page * 20 >= total || loading}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}