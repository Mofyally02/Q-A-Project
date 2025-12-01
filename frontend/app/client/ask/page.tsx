'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Upload, X, Loader2, Sparkles, Home, Clock, MessageSquare, TrendingUp, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function AskQuestionPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    subject: '',
    question_text: '',
    priority: 'normal',
    file: null as File | null
  })
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only')
      return
    }
  }, [user, isAuthenticated, router])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setForm({ ...form, file })
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onloadend = () => setPreview(reader.result as string)
        reader.readAsDataURL(file)
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.question_text) {
      toast.error('Please enter your question')
      return
    }

    try {
      setLoading(true)
      const formData = new FormData()
      formData.append('question_text', form.question_text)
      if (form.subject) {
        formData.append('subject', form.subject)
      }
      formData.append('priority', form.priority)
      if (form.file) {
        formData.append('images', form.file)
      }

      const response: any = await apiHelpers.askQuestion(formData)
      if (response.data?.success || response.data?.question_id) {
        const questionId = response.data?.question_id || response.data?.data?.question_id
        toast.success('Question submitted successfully!')
        router.push(`/client/chat/${questionId}`)
      } else {
        toast.error('Failed to submit question')
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to submit question')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg flex-shrink-0">
          <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">Ask a Question</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">Get instant answers from AI-powered experts</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        <div className="glass bg-card/60 rounded-lg sm:rounded-lg border shadow-soft p-4 sm:p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Subject <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={form.subject}
              onChange={(e) => setForm({ ...form, subject: e.target.value })}
              placeholder="e.g., Calculus - Derivatives"
              className="w-full px-4 py-3 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Question <span className="text-destructive">*</span>
            </label>
            <textarea
              value={form.question_text}
              onChange={(e) => setForm({ ...form, question_text: e.target.value })}
              placeholder="Describe your question in detail..."
              rows={10}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Priority
            </label>
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Attach File (Optional)
            </label>
            <div className="mt-1 flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg cursor-pointer bg-background/50 hover:bg-background/70 transition-colors">
                <Upload className="w-4 h-4 text-foreground/70" />
                <span className="text-sm text-foreground/80">Choose File</span>
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  accept="image/*,.pdf,.doc,.docx"
                />
              </label>
              {form.file && (
                <div className="flex items-center gap-2 text-sm text-foreground/80">
                  <span>{form.file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setForm({ ...form, file: null })
                      setPreview(null)
                    }}
                    className="p-1"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>
            {preview && (
              <div className="mt-4">
                <img src={preview} alt="Preview" className="max-w-md rounded-lg border border-border shadow-soft" />
              </div>
            )}
          </div>

          <div className="flex items-center justify-end gap-4 pt-4 border-t border-border">
            <Link href="/client/dashboard" passHref>
              <Button variant="ghost" className="px-6 py-2.5 text-sm">
                Cancel
              </Button>
            </Link>
            <Button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 text-sm flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Submit Question
                </>
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}