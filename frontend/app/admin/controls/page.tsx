'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Zap, 
  Search, 
  RefreshCw, 
  UserCheck, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Send,
  Loader2,
  ArrowRight
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function AdminControlsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [questionId, setQuestionId] = useState('')
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null)
  const [experts, setExperts] = useState<any[]>([])
  const [reassignExpertId, setReassignExpertId] = useState('')
  const [reassignReason, setReassignReason] = useState('')
  const [activeTab, setActiveTab] = useState('search')

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
    loadExperts()
  }, [user, router])

  const loadExperts = async () => {
    try {
      const response = await apiHelpers.getUsers({ role: 'expert' })
      if (response.data?.success) {
        setExperts(response.data.data?.users || [])
      }
    } catch (error) {
      console.error('Error loading experts:', error)
    }
  }

  const searchQuestion = async () => {
    if (!questionId) {
      toast.error('Please enter a question ID')
      return
    }
    
    try {
      setLoading(true)
      const response = await apiHelpers.getQuestionStatus(questionId)
      if (response.data?.success) {
        setSelectedQuestion(response.data.data)
      } else {
        toast.error(response.data?.message || 'Question not found')
        setSelectedQuestion(null)
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to find question')
      setSelectedQuestion(null)
    } finally {
      setLoading(false)
    }
  }

  const handleReassign = async () => {
    if (!selectedQuestion || !reassignExpertId || !reassignReason) {
      toast.error('Please fill all fields')
      return
    }
    
    try {
      setLoading(true)
      await apiHelpers.reassignQuestion(selectedQuestion.question_id, {
        expert_id: reassignExpertId,
        reason: reassignReason
      })
      toast.success('Question reassigned successfully')
      setReassignExpertId('')
      setReassignReason('')
      await searchQuestion()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to reassign')
    } finally {
      setLoading(false)
    }
  }

  const handleForceDeliver = async () => {
    if (!selectedQuestion) {
      toast.error('Please search for a question first')
      return
    }
    
    try {
      setLoading(true)
      await apiHelpers.forceDeliver(selectedQuestion.question_id)
      toast.success('Question force delivered')
      await searchQuestion()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to force deliver')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'success' | 'warning' | 'info' | 'outline' | 'error'> = {
      submitted: 'default',
      processing: 'secondary',
      review: 'default',
      delivered: 'success',
      rated: 'success'
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
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <Zap className="w-8 h-8 text-primary" />
            Workflow Controls
          </h1>
          <p className="text-muted-foreground mt-2">
            Override workflows, reassign questions, and manage platform operations
          </p>
        </div>
        <Button variant="outline" onClick={() => router.push('/admin/dashboard')}>
          Back to Dashboard
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="search">Search & Manage</TabsTrigger>
          <TabsTrigger value="reassign">Reassign Question</TabsTrigger>
          <TabsTrigger value="override">Override Actions</TabsTrigger>
        </TabsList>

        {/* Search & Manage Tab */}
        <TabsContent value="search" className="space-y-6">
          <Card className="glass border-border/50 p-6">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Enter question ID..."
                  value={questionId}
                  onChange={(e) => setQuestionId(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchQuestion()}
                  className="bg-background/50 border-border/50"
                />
              </div>
              <Button onClick={searchQuestion} disabled={loading || !questionId}>
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </Button>
            </div>
          </Card>

          {selectedQuestion && (
            <Card className="glass border-border/50 p-6">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">Question Details</h3>
                    <p className="text-sm text-muted-foreground mt-1">ID: {selectedQuestion.question_id}</p>
                  </div>
                  {getStatusBadge(selectedQuestion.status)}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Client</p>
                    <p className="text-foreground font-medium">{selectedQuestion.client_email || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Subject</p>
                    <p className="text-foreground font-medium">{selectedQuestion.subject || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Created</p>
                    <p className="text-foreground font-medium">
                      {new Date(selectedQuestion.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Expert</p>
                    <p className="text-foreground font-medium">{selectedQuestion.expert_id || 'Unassigned'}</p>
                  </div>
                </div>

                {selectedQuestion.content && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Content Preview</p>
                    <div className="p-4 rounded-lg bg-background/50 border border-border/30">
                      <p className="text-sm text-foreground line-clamp-3">
                        {typeof selectedQuestion.content === 'string' 
                          ? selectedQuestion.content 
                          : JSON.stringify(selectedQuestion.content)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </TabsContent>

        {/* Reassign Tab */}
        <TabsContent value="reassign" className="space-y-6">
          <Card className="glass border-border/50 p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Reassign Question to Expert</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Question ID
                </label>
                <Input
                  placeholder="Enter question ID..."
                  value={questionId}
                  onChange={(e) => setQuestionId(e.target.value)}
                  className="bg-background/50 border-border/50"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Select Expert
                </label>
                <select
                  value={reassignExpertId}
                  onChange={(e) => setReassignExpertId(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground"
                >
                  <option value="">Select an expert...</option>
                  {experts.map((expert) => (
                    <option key={expert.user_id} value={expert.user_id}>
                      {expert.email} ({expert.first_name} {expert.last_name})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Reason for Reassignment
                </label>
                <Textarea
                  placeholder="Explain why this question is being reassigned..."
                  value={reassignReason}
                  onChange={(e) => setReassignReason(e.target.value)}
                  className="bg-background/50 border-border/50 min-h-[100px]"
                />
              </div>
              <Button 
                onClick={handleReassign} 
                disabled={loading || !questionId || !reassignExpertId || !reassignReason}
                className="w-full"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="w-4 h-4 mr-2" />
                )}
                Reassign Question
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* Override Actions Tab */}
        <TabsContent value="override" className="space-y-6">
          <Card className="glass border-border/50 p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Override Actions</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Use these actions to override normal workflow processes. Use with caution.
            </p>
            
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-warning/10 border border-warning/30">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-warning mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground mb-1">Force Deliver</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      Immediately deliver a question to the client, bypassing all checks.
                    </p>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Question ID..."
                        value={questionId}
                        onChange={(e) => setQuestionId(e.target.value)}
                        className="flex-1 bg-background/50 border-border/50"
                      />
                      <Button 
                        onClick={handleForceDeliver}
                        disabled={loading || !questionId}
                        variant="outline"
                      >
                        {loading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
