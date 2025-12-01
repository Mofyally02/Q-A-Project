'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MessageSquare, Loader2, Send, Search, User, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'

export default function AdminMessagesPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [messages, setMessages] = useState<any[]>([])
  const [selectedMessage, setSelectedMessage] = useState<any>(null)
  const [replyText, setReplyText] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

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
    loadMessages()
  }, [user, router])

  const loadMessages = async () => {
    try {
      setLoading(true)
      // Use notifications endpoint for admin messages
      const response = await apiHelpers.getAdminNotifications({})
      if (response.data?.success) {
        setMessages(response.data.data?.notifications || [])
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load messages')
    } finally {
      setLoading(false)
    }
  }

  const handleSendReply = async () => {
    if (!replyText.trim() || !selectedMessage) return
    
    try {
      // Use notifications broadcast endpoint
      await apiHelpers.sendNotification({
        recipient_type: 'specific',
        recipient_ids: [selectedMessage.user_id],
        subject: 'Re: ' + (selectedMessage.subject || 'Message'),
        message: replyText
      })
      toast.success('Message sent')
      setReplyText('')
      loadMessages()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to send message')
    }
  }

  const filteredMessages = messages.filter(msg => {
    return !searchQuery || 
      msg.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      msg.message?.toLowerCase().includes(searchQuery.toLowerCase())
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading messages...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Admin Messages</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Messages List */}
        <Card className="lg:col-span-1 p-4">
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search messages..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredMessages.length > 0 ? (
                filteredMessages.map((msg) => (
                  <div
                    key={msg.notification_id}
                    onClick={() => setSelectedMessage(msg)}
                    className={`p-4 rounded-lg cursor-pointer transition-colors ${
                      selectedMessage?.notification_id === msg.notification_id
                        ? 'bg-primary/10 border border-primary/20'
                        : 'bg-background/50 border border-border/30 hover:bg-accent/50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium text-foreground">
                          {msg.user_id?.slice(0, 8) || 'User'}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {msg.type || 'Message'}
                      </Badge>
                    </div>
                    <p className="text-sm text-foreground font-semibold mb-1 line-clamp-1">
                      {msg.subject || 'No subject'}
                    </p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {msg.message || 'No message'}
                    </p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {new Date(msg.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No messages found</p>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Message Detail & Reply */}
        <Card className="lg:col-span-2 p-6">
          {selectedMessage ? (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4">
                  {selectedMessage.subject || 'No Subject'}
                </h2>
                <div className="space-y-2 text-sm text-muted-foreground mb-4">
                  <p>From: User #{selectedMessage.user_id?.slice(0, 8)}</p>
                  <p>Date: {new Date(selectedMessage.created_at).toLocaleString()}</p>
                </div>
                <div className="p-4 bg-background/50 rounded-lg border border-border/30">
                  <p className="text-foreground whitespace-pre-wrap">
                    {selectedMessage.message || 'No message content'}
                  </p>
                </div>
              </div>

              <div className="pt-6 border-t border-border">
                <h3 className="text-lg font-semibold text-foreground mb-4">Reply</h3>
                <div className="space-y-4">
                  <Textarea
                    placeholder="Type your reply..."
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    className="min-h-[150px]"
                  />
                  <Button
                    onClick={handleSendReply}
                    disabled={!replyText.trim()}
                    className="w-full"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Send Reply
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full min-h-[400px] text-muted-foreground">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Select a message to view and reply</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

