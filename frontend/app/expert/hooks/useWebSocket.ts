'use client'

import { useEffect, useRef } from 'react'
import { playAdminNotificationSound } from '@/app/client/lib/sounds'
import toast from 'react-hot-toast'

export function useExpertWebSocket(url?: string) {
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Only connect if URL is provided
    if (!url) return

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('Expert WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          handleMessage(msg)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('Expert WebSocket disconnected')
      }

      wsRef.current = ws

      return () => {
        if (wsRef.current) {
          wsRef.current.close()
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [url])

  const handleMessage = (msg: any) => {
    switch (msg.type) {
      case 'expert_assignment':
        toast.success(`New question assigned: ${msg.subject}`)
        // R2.mp3 for admin-to-expert notifications
        playAdminNotificationSound()
        break

      case 'notification':
        toast(msg.message || 'New notification')
        // R2.mp3 for admin notifications to experts
        playAdminNotificationSound()
        break

      case 'question_updated':
        toast('Question status updated')
        break

      default:
        console.log('Unknown message type:', msg.type)
    }
  }

  return wsRef.current
}


