'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  TestTube, 
  Loader2, 
  CheckCircle, 
  XCircle,
  Search,
  AlertCircle,
  Zap
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'

export default function AdminTestPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [testForm, setTestForm] = useState({
    content: '',
    subject: 'Test Question',
    type: 'text',
    test_reason: 'API key verification'
  })
  const [testQuestion, setTestQuestion] = useState<any>(null)
  const [questionId, setQuestionId] = useState('')

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
  }, [user, router])

  const handleSubmitTest = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      const response = await apiHelpers.submitTestQuestion(testForm)
      if (response.data?.success) {
        toast.success('Test question submitted successfully')
        setQuestionId(response.data.data.question_id)
        setTestQuestion(response.data.data)
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to submit test question')
    } finally {
      setLoading(false)
    }
  }

  const handleCheckStatus = async () => {
    if (!questionId) {
      toast.error('Please enter a question ID')
      return
    }
    try {
      setLoading(true)
      const response = await apiHelpers.getTestQuestionStatus(questionId)
      if (response.data?.success) {
        setTestQuestion(response.data.data)
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to get test status')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'success' | 'warning' | 'info' | 'outline' | 'error'> = {
      healthy: 'success',
      error: 'error',
      processing: 'warning',
      delivered: 'success'
    }
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status}
      </Badge>
    )
  }

  return (
    <div className="w-full space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 w-full">
        <div>
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground flex items-center gap-2 sm:gap-3">
            <TestTube className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-primary" />
            System Testing
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-1 sm:mt-2">
            Test system functionality and verify API key connectivity
          </p>
        </div>
        <Button variant="outline" onClick={() => router.push('/admin/dashboard')}>
          Back to Dashboard
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Submit Test Question */}
        <Card className="glass border-border/50 p-4 sm:p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            Submit Test Question
          </h3>
          <form onSubmit={handleSubmitTest} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Subject
              </label>
              <Input
                type="text"
                value={testForm.subject}
                onChange={(e) => setTestForm((prev) => ({ ...prev, subject: e.target.value }))}
                placeholder="Test question subject"
                className="bg-background/50 border-border/50"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Content
              </label>
              <Textarea
                value={testForm.content}
                onChange={(e) => setTestForm((prev) => ({ ...prev, content: e.target.value }))}
                placeholder="Question content"
                className="bg-background/50 border-border/50 min-h-[150px]"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Test Reason
              </label>
              <Input
                type="text"
                value={testForm.test_reason}
                onChange={(e) => setTestForm((prev) => ({ ...prev, test_reason: e.target.value }))}
                placeholder="Reason for testing"
                className="bg-background/50 border-border/50"
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <TestTube className="w-4 h-4 mr-2" />
                  Submit Test Question
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* Check Test Status */}
        <Card className="glass border-border/50 p-4 sm:p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            Check Test Status
          </h3>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                type="text"
                value={questionId}
                onChange={(e) => setQuestionId(e.target.value)}
                placeholder="Enter question ID..."
                className="flex-1 bg-background/50 border-border/50"
              />
              <Button onClick={handleCheckStatus} disabled={loading || !questionId}>
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </Button>
            </div>

            {testQuestion && (
              <div className="p-4 rounded-lg bg-background/50 border border-border/30 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-foreground">Test Question Status</h4>
                    <p className="text-xs text-muted-foreground">ID: {testQuestion.question_id}</p>
                  </div>
                  {getStatusBadge(testQuestion.system_status || testQuestion.status)}
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground">Status</p>
                    <p className="font-medium text-foreground">{testQuestion.status}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Subject</p>
                    <p className="font-medium text-foreground">{testQuestion.subject}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">AI Response</p>
                    <p className="font-medium text-foreground">
                      {testQuestion.has_ai_response ? (
                        <CheckCircle className="w-4 h-4 text-success inline" />
                      ) : (
                        <XCircle className="w-4 h-4 text-muted-foreground inline" />
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Humanized</p>
                    <p className="font-medium text-foreground">
                      {testQuestion.has_humanized_response ? (
                        <CheckCircle className="w-4 h-4 text-success inline" />
                      ) : (
                        <XCircle className="w-4 h-4 text-muted-foreground inline" />
                      )}
                    </p>
                  </div>
                  {testQuestion.confidence_score && (
                    <div>
                      <p className="text-muted-foreground">Confidence</p>
                      <p className="font-medium text-foreground">{testQuestion.confidence_score}</p>
                    </div>
                  )}
                  {testQuestion.ai_content_percentage && (
                    <div>
                      <p className="text-muted-foreground">AI Content</p>
                      <p className="font-medium text-foreground">{testQuestion.ai_content_percentage}%</p>
                    </div>
                  )}
                </div>

                {testQuestion.message && (
                  <div className="p-3 rounded-lg bg-warning/10 border border-warning/30">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-warning mt-0.5" />
                      <p className="text-sm text-foreground">{testQuestion.message}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
