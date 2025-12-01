'use client'

import { useEffect, useRef } from 'react'
import { useRealTimeStore } from '@/stores/useRealTimeStore'
import { playAnswerDeliveredSound, playAdminNotificationSound, NotificationSource } from '@/app/client/lib/sounds'
import toast from 'react-hot-toast'

export function useWebSocket(url?: string) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const {
    addLiveQuestion,
    updateQuestionStatus,
    addRecentAnswer,
    incrementNotifications,
    setCredits
  } = useRealTimeStore()

  useEffect(() => {
    // Only connect if URL is provided and we're in the browser
    if (!url || typeof window === 'undefined') return

    // Don't connect if WebSocket is not supported
    if (!('WebSocket' in window)) {
      console.warn('WebSocket is not supported in this browser')
      return
    }

    let shouldReconnect = true
    let reconnectAttempts = 0
    const maxReconnectAttempts = 5
    const reconnectDelay = 3000

    const connect = () => {
      // Clear any existing connection
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }

      // Clear any pending reconnect
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }

      try {
        const ws = new WebSocket(url)

        ws.onopen = () => {
          console.log('WebSocket connected')
          reconnectAttempts = 0 // Reset on successful connection
        }

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data)
            handleMessage(msg)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        ws.onerror = (event) => {
          // WebSocket error events don't provide much info, just log a warning
          // Don't log empty objects to console
          if (process.env.NODE_ENV === 'development') {
            console.warn('WebSocket connection error. This is normal if the WebSocket server is not running.')
          }
        }

        ws.onclose = (event) => {
          console.log('WebSocket disconnected', event.code, event.reason)
          
          // Only attempt to reconnect if it wasn't a manual close and we haven't exceeded max attempts
          if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++
            console.log(`Attempting to reconnect WebSocket (${reconnectAttempts}/${maxReconnectAttempts})...`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              if (shouldReconnect) {
                connect()
              }
            }, reconnectDelay)
          } else if (reconnectAttempts >= maxReconnectAttempts) {
            console.warn('WebSocket: Max reconnection attempts reached. WebSocket will not reconnect.')
          }
        }

        wsRef.current = ws
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error)
        // Don't attempt to reconnect on initial connection failure
        shouldReconnect = false
      }
    }

    // Initial connection
    connect()

    return () => {
      shouldReconnect = false
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [url])

  const handleMessage = (msg: any) => {
    switch (msg.type) {
      case 'question_submitted':
        addLiveQuestion({
          id: msg.question_id,
          subject: msg.subject,
          status: 'processing',
          timestamp: msg.timestamp || new Date().toISOString()
        })
        toast.success('Question submitted!')
        break

      case 'ai_processing_started':
        updateQuestionStatus(msg.question_id, { status: 'processing' })
        break

      case 'humanization_complete':
        updateQuestionStatus(msg.question_id, { status: 'reviewing' })
        break

      case 'expert_assigned':
        updateQuestionStatus(msg.question_id, {
          status: 'reviewing',
          expert: {
            name: msg.expert_name || 'Expert',
            avatar: msg.expert_avatar
          }
        })
        break

      case 'expert_typing':
        updateQuestionStatus(msg.question_id, { status: 'typing' })
        break

      case 'answer_delivered':
        addRecentAnswer({
          id: msg.question_id,
          question: msg.question || msg.subject,
          answer: msg.answer,
          expert: msg.expert_name || 'Expert',
          subject: msg.subject || 'General',
          timestamp: msg.timestamp || new Date().toISOString(),
          image: msg.image,
          rating: msg.rating
        })
        toast.success('New answer delivered!', {
          icon: '🎉'
        })
        // Play R1.mp3 for expert-to-client answer delivery
        playAnswerDeliveredSound()
        break

      case 'notification':
        incrementNotifications()
        const notificationSource: NotificationSource = msg.source || 'system'
        toast(msg.message || 'New notification')
        // Play appropriate sound based on notification source
        if (notificationSource === 'expert') {
          playAnswerDeliveredSound() // R1.mp3 for expert notifications
        } else {
          playAdminNotificationSound() // R2.mp3 for admin/system notifications
        }
        break

      case 'credit_added':
        setCredits(msg.credits)
        toast.success(`Credits updated: ${msg.credits}`)
        break

      default:
        console.log('Unknown message type:', msg.type)
    }
  }

  return wsRef.current
}

