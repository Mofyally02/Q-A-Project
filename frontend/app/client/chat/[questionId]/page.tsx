
'use client'

import { MessageSquare, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import toast from 'react-hot-toast'

// Mock imports
// import { useAuthStore } from '@/stores/authStore'
// import { apiHelpers } from '@/lib/api'
// import { UserRole } from '@/lib/types'

import { Button } from '../../components/ui/button'
import { cn } from '../../lib/utils'

export default function ClientChatPage() {
  const router = useRouter()
  const params = useParams()
  const questionId = params.questionId as string
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [chatThread, setChatThread] = useState<any>(null) // Replace with actual type

  // Mock user and apiHelpers
  const user = { role: 'client', id: 'mock-client-id' }
  const apiHelpers = {
    getChatThread: async (id: string) => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                question_id: id,
                subject: 'Mock Chat Subject',
                status: 'delivered',
                messages: [
                  { type: 'question', content: 'What is the capital of France?', timestamp: new Date().toISOString(), from: 'client' },
                  { type: 'answer', content: 'The capital of France is Paris.', timestamp: new Date().toISOString(), from: 'expert' },
                ]
              }
            }
          })
        }, 800)
      })
    }
  }

  useEffect(() => {
    // if (!user || user.role !== UserRole.CLIENT) {
    //   router.push('/login')
    //   toast.error('Client access only.')
    //   return
    // }

    if (questionId) {
      const fetchChatThread = async () => {
        try {
          setLoading(true)
          const response: any = await apiHelpers.getChatThread(questionId)
          if (response.data.success) {
            setChatThread(response.data.data)
          } else {
            toast.error(response.data.message || 'Failed to load chat thread.')
          }
        } catch (error) {
          toast.error('An error occurred while fetching chat data.')
        } finally {
          setLoading(false)
        }
      }
      fetchChatThread()
    }
  }, [questionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!chatThread) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <MessageSquare className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
        <p>No chat thread found.</p>
      </div>
    )
  }

  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft flex items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg">
          <MessageSquare className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Live Answer Chat</h1>
          <p className="text-muted-foreground mt-1">Subject: {chatThread.subject}</p>
        </div>
      </div>

      <div className="glass bg-card/60 rounded-lg border shadow-soft p-6 h-[60vh] flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {chatThread.messages.map((msg: any, index: number) => (
            <div
              key={index}
              className={`flex ${msg.from === 'client' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={cn(
                  "max-w-[70%] p-3 rounded-lg shadow-sm",
                  msg.from === 'client'
                    ? 'bg-primary text-primary-foreground rounded-br-none'
                    : 'bg-muted text-muted-foreground rounded-bl-none'
                )}
              >
                <p>{msg.content}</p>
                <span className="block text-xs opacity-75 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="border-t border-border pt-4">
          <input
            type="text"
            placeholder="Type your message..."
            className="w-full px-4 py-2 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
            disabled // For now, as this is a placeholder for real-time chat
          />
        </div>
      </div>
      </div>
    </div>
  )
}

