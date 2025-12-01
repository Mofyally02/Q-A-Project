'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Ticket, Send, Loader2, ArrowLeft, MessageSquare, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface Ticket {
  id: string
  subject: string
  message: string
  status: 'pending' | 'open' | 'closed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  created_at: string
  updated_at: string
  admin_response?: string
}

export default function ClientTicketsPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    priority: 'normal' as 'low' | 'normal' | 'high' | 'urgent'
  })

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only')
      return
    }
    loadTickets()
  }, [user, isAuthenticated, router])

  const loadTickets = async () => {
    try {
      setLoading(true)
      // Try different possible API endpoints
      const response: any = await apiHelpers.getTickets().catch(() => 
        apiHelpers.getClientTicket().catch(() => null)
      )
      
      if (response?.data?.tickets || response?.data?.data || response?.data?.ticket) {
        const ticketData = response.data.tickets || response.data.data || 
                          (response.data.ticket ? [response.data.ticket] : [])
        setTickets(Array.isArray(ticketData) ? ticketData : [])
      } else {
        setTickets([])
      }
    } catch (error: any) {
      console.error('Error loading tickets:', error)
      setTickets([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.subject.trim() || !formData.message.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      setSubmitting(true)
      // Try createTicket first, fallback to createSupportTicket
      const response: any = await apiHelpers.createTicket(formData).catch(() => 
        apiHelpers.createSupportTicket({
          subject: formData.subject,
          description: formData.message
        })
      )
      
      if (response?.data?.success || response?.data?.ticket_id) {
        toast.success('Ticket created successfully! An admin will respond soon.')
        setFormData({ subject: '', message: '', priority: 'normal' })
        setShowCreateForm(false)
        await loadTickets()
        
        // Optionally navigate to messages if ticket is auto-opened
        if (response?.data?.auto_open) {
          setTimeout(() => {
            router.push('/client/messages')
          }, 1500)
        }
      } else {
        toast.error('Failed to create ticket')
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to create ticket'
      toast.error(errorMessage)
      console.error('Create ticket error:', error)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/client/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
              <Ticket className="w-6 h-6 text-primary" />
              Support Tickets
            </h1>
            <p className="text-muted-foreground mt-1">Create a ticket to start a conversation with admin</p>
          </div>
        </div>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Ticket className="w-4 h-4 mr-2" />
          {showCreateForm ? 'Cancel' : 'Create Ticket'}
        </Button>
      </div>

      {/* Create Ticket Form */}
      {showCreateForm && (
        <Card className="p-6 animate-fade-in">
          <h2 className="text-xl font-semibold text-foreground mb-4">Create New Ticket</h2>
          <form onSubmit={handleCreateTicket} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Subject <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="e.g., Question about billing, Need help with..."
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Message <span className="text-destructive">*</span>
              </label>
              <textarea
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                placeholder="Describe your question or issue in detail..."
                rows={6}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary resize-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <Button type="submit" disabled={submitting} className="flex-1">
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Create Ticket
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false)
                  setFormData({ subject: '', message: '', priority: 'normal' })
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Tickets List */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Your Tickets</h2>
        {tickets.length === 0 ? (
          <div className="text-center py-12">
            <Ticket className="w-16 h-16 mx-auto text-muted-foreground opacity-50 mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No tickets yet</h3>
            <p className="text-muted-foreground mb-4">Create a ticket to start a conversation with admin</p>
            <Button onClick={() => setShowCreateForm(true)}>
              <Ticket className="w-4 h-4 mr-2" />
              Create Your First Ticket
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {tickets.map((ticket) => (
              <div
                key={ticket.id}
                className={cn(
                  "p-4 rounded-lg border transition-all duration-200",
                  ticket.status === 'open' 
                    ? "bg-primary/5 border-primary/20" 
                    : ticket.status === 'closed'
                    ? "bg-muted/30 border-border"
                    : "bg-background border-border hover:border-primary/50"
                )}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-foreground">{ticket.subject}</h3>
                      <span className={cn(
                        "px-2 py-0.5 rounded-full text-xs font-medium",
                        ticket.status === 'open' && "bg-green-500/20 text-green-600 dark:text-green-400",
                        ticket.status === 'pending' && "bg-yellow-500/20 text-yellow-600 dark:text-yellow-400",
                        ticket.status === 'closed' && "bg-muted text-muted-foreground"
                      )}>
                        {ticket.status}
                      </span>
                      <span className={cn(
                        "px-2 py-0.5 rounded-full text-xs font-medium",
                        ticket.priority === 'urgent' && "bg-red-500/20 text-red-600 dark:text-red-400",
                        ticket.priority === 'high' && "bg-orange-500/20 text-orange-600 dark:text-orange-400",
                        ticket.priority === 'normal' && "bg-blue-500/20 text-blue-600 dark:text-blue-400",
                        ticket.priority === 'low' && "bg-gray-500/20 text-gray-600 dark:text-gray-400"
                      )}>
                        {ticket.priority}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{ticket.message}</p>
                    <p className="text-xs text-muted-foreground">
                      Created {new Date(ticket.created_at).toLocaleString()}
                    </p>
                    {ticket.admin_response && (
                      <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                        <p className="text-xs font-semibold text-foreground mb-1">Admin Response:</p>
                        <p className="text-sm text-foreground">{ticket.admin_response}</p>
                      </div>
                    )}
                  </div>
                  {ticket.status === 'open' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push('/client/messages')}
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Chat
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

