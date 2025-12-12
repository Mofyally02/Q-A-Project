'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Send, MessageSquare, Loader2, ArrowLeft, Ticket, X, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  message: string
  sender: 'client' | 'admin'
  sender_name?: string
  created_at: string
  read: boolean
}

interface Ticket {
  id: string
  subject: string
  description: string
  status: 'pending' | 'open' | 'closed'
  created_at: string
  updated_at: string
}

export default function ClientMessagesPage() {
  const router = useRouter()
  const { user, isAuthenticated, isHydrated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [showTicketModal, setShowTicketModal] = useState(false)
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    description: ''
  })
  const [creatingTicket, setCreatingTicket] = useState(false)
  const [newMessage, setNewMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

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
    loadTicket()
  }, [user, isAuthenticated, isHydrated, router])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadTicket = async () => {
    try {
      setLoading(true)
      // Check if client has an active ticket
      const response: any = await apiHelpers.getClientTicket().catch(() => null)
      
      if (response?.data?.ticket) {
        const ticketData = response.data.ticket || response.data.data
        setTicket(ticketData)
        // Load messages for this ticket
        if (ticketData.id) {
          await loadMessages(ticketData.id)
        }
      } else {
        // No active ticket - show ticket creation modal
        setShowTicketModal(true)
        setTicket(null)
        setMessages([])
      }
    } catch (error: any) {
      console.error('Error loading ticket:', error)
      // Show ticket modal if no ticket exists
      setShowTicketModal(true)
      setTicket(null)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (ticketId: string) => {
    try {
      const response: any = await apiHelpers.getAdminMessages().catch(() => null)
      
      if (response?.data?.messages || response?.data?.data?.messages) {
        const messageData = response.data.messages || response.data.data.messages
        setMessages(Array.isArray(messageData) ? messageData : [])
      } else {
        setMessages([])
      }
    } catch (error: any) {
      console.error('Error loading messages:', error)
      setMessages([])
    }
  }

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticketForm.subject.trim() || !ticketForm.description.trim()) {
      toast.error('Please fill in all fields')
      return
    }

    try {
      setCreatingTicket(true)
      const response: any = await apiHelpers.createSupportTicket({
        subject: ticketForm.subject,
        description: ticketForm.description
      })

      if (response?.data?.ticket || response?.data?.data?.ticket) {
        const ticketData = response.data.ticket || response.data.data.ticket
        setTicket(ticketData)
        setShowTicketModal(false)
        setTicketForm({ subject: '', description: '' })
        toast.success('Ticket created successfully! An admin will respond soon.')
        // Load messages for the new ticket
        if (ticketData.id) {
          await loadMessages(ticketData.id)
        }
      } else {
        toast.error('Failed to create ticket')
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to create ticket'
      toast.error(errorMessage)
      console.error('Create ticket error:', error)
    } finally {
      setCreatingTicket(false)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim()) {
      toast.error('Please enter a message')
      return
    }

    if (!ticket) {
      toast.error('Please create a ticket first')
      setShowTicketModal(true)
      return
    }

    try {
      setSending(true)
      
      // Create optimistic message
      const tempMessage: Message = {
        id: `temp-${Date.now()}`,
        message: newMessage,
        sender: 'client',
        sender_name: user?.first_name || 'You',
        created_at: new Date().toISOString(),
        read: false
      }
      
      setMessages([...messages, tempMessage])
      setNewMessage('')
      
      // Send to backend
      try {
        const response: any = await apiHelpers.sendMessageToAdmin({ 
          message: newMessage,
          ticket_id: ticket.id
        })
        if (response?.data?.success || response?.data?.message_id) {
          if (response.data.message) {
            setMessages([...messages, response.data.message])
          } else {
            setMessages([...messages, tempMessage])
          }
          toast.success('Message sent!')
        } else {
          setMessages(messages)
          toast.error('Failed to send message. Please try again.')
        }
      } catch (error: any) {
        setMessages(messages)
        const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to send message'
        toast.error(errorMessage)
        console.error('Send message error:', error)
      }
    } catch (error: any) {
      toast.error('Failed to send message')
      console.error('Send message error:', error)
    } finally {
      setSending(false)
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
              <MessageSquare className="w-6 h-6 text-primary" />
              Live Chat with Admin
            </h1>
            <p className="text-muted-foreground mt-1">
              {ticket ? `Ticket #${ticket.id.slice(0, 8)} - ${ticket.status}` : 'Create a ticket to start chatting'}
            </p>
          </div>
        </div>
        {ticket && (
          <div className="flex items-center gap-2">
            <span className={cn(
              "px-3 py-1 rounded-full text-xs font-medium",
              ticket.status === 'open' ? "bg-green-500/10 text-green-500" :
              ticket.status === 'pending' ? "bg-yellow-500/10 text-yellow-500" :
              "bg-gray-500/10 text-gray-500"
            )}>
              {ticket.status.toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Ticket Creation Modal */}
      {showTicketModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 relative">
            <button
              onClick={() => setShowTicketModal(false)}
              className="absolute top-4 right-4 p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Ticket className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-foreground">Create Support Ticket</h2>
                <p className="text-sm text-muted-foreground">Start a conversation with our admin team</p>
              </div>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Subject <span className="text-destructive">*</span>
                </label>
                <input
                  type="text"
                  value={ticketForm.subject}
                  onChange={(e) => setTicketForm({ ...ticketForm, subject: e.target.value })}
                  placeholder="e.g., Question about billing"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Description <span className="text-destructive">*</span>
                </label>
                <textarea
                  value={ticketForm.description}
                  onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
                  placeholder="Describe your question or issue..."
                  rows={5}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary resize-none"
                  required
                />
              </div>

              <div className="flex items-center gap-2 p-3 bg-blue-500/10 rounded-lg">
                <AlertCircle className="w-4 h-4 text-blue-500 flex-shrink-0" />
                <p className="text-xs text-blue-500">
                  An admin will review your ticket and respond as soon as possible.
                </p>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowTicketModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={creatingTicket}
                  className="flex-1"
                >
                  {creatingTicket ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Ticket className="w-4 h-4 mr-2" />
                      Create Ticket
                    </>
                  )}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Messages Container - Only show if ticket exists */}
      {ticket ? (
        <Card className="p-6 h-[calc(100vh-20rem)] flex flex-col">
          {/* Ticket Info */}
          <div className="mb-4 p-3 bg-muted/50 rounded-lg border border-border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground">Ticket: {ticket.subject}</p>
                <p className="text-xs text-muted-foreground mt-1">{ticket.description}</p>
              </div>
              <span className={cn(
                "px-2 py-1 rounded text-xs font-medium",
                ticket.status === 'open' ? "bg-green-500/10 text-green-500" :
                ticket.status === 'pending' ? "bg-yellow-500/10 text-yellow-500" :
                "bg-gray-500/10 text-gray-500"
              )}>
                {ticket.status}
              </span>
            </div>
          </div>

          {/* Messages List */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12">
                <MessageSquare className="w-16 h-16 text-muted-foreground opacity-50 mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No messages yet</h3>
                <p className="text-muted-foreground">Start the conversation by sending a message</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex",
                    message.sender === 'client' ? "justify-end" : "justify-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[70%] rounded-lg p-4",
                      message.sender === 'client'
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold opacity-80">
                        {message.sender_name || (message.sender === 'client' ? 'You' : 'Admin')}
                      </span>
                      <span className="text-xs opacity-60">
                        {new Date(message.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex items-center gap-2 pt-4 border-t border-border">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary"
              disabled={sending || ticket.status === 'closed'}
            />
            <Button
              type="submit"
              disabled={sending || !newMessage.trim() || ticket.status === 'closed'}
              className="flex-shrink-0"
            >
              {sending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Send
                </>
              )}
            </Button>
          </form>
        </Card>
      ) : (
        <Card className="p-12 text-center">
          <Ticket className="w-16 h-16 mx-auto text-muted-foreground opacity-50 mb-4" />
          <h3 className="text-xl font-semibold text-foreground mb-2">No Active Ticket</h3>
          <p className="text-muted-foreground mb-6">Create a ticket to start chatting with our admin team</p>
          <Button onClick={() => setShowTicketModal(true)}>
            <Ticket className="w-4 h-4 mr-2" />
            Create Ticket
          </Button>
        </Card>
      )}
    </div>
  )
}
