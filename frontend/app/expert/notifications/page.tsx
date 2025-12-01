
'use client'

import { Bell, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function ExpertNotificationsPage() {
  const router = useRouter()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [notifications, setNotifications] = useState<any[]>([]) // Replace with actual type

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getNotifications: async () => { // Assuming same API endpoint for experts and clients
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                notifications: [
                  { id: 'n1', title: 'New Task Assigned!', message: 'A new question is waiting for your review.', createdAt: new Date().toISOString(), read: false },
                  { id: 'n2', title: 'Client Follow-up', message: 'Client has a question on your last answer.', createdAt: new Date().toISOString(), read: true },
                ]
              }
            }
          })
        }, 800)
      })
    },
    markNotificationRead: async (id: string) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ data: { success: true } })
            }, 300)
        })
    },
    markAllNotificationsRead: async () => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ data: { success: true } })
            }, 300)
        })
    }
  }

  useEffect(() => {
    // if (!user || user.role !== UserRole.EXPERT) {
    //   router.push('/login')
    //   toast.error('Expert access only.')
    //   return
    // }

    const fetchNotifications = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getNotifications()
        if (response.data.success) {
          setNotifications(response.data.data.notifications)
        } else {
          toast.error(response.data.message || 'Failed to load notifications.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching notifications.')
      } finally {
        setLoading(false)
      }
    }
    fetchNotifications()
  }, [])

  const handleMarkRead = async (id: string) => {
    try {
      await apiHelpers.markNotificationRead(id)
      setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n))
      toast.success('Notification marked as read.')
    } catch (error) {
      toast.error('Failed to mark notification as read.')
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await apiHelpers.markAllNotificationsRead()
      setNotifications(notifications.map(n => ({ ...n, read: true })))
      toast.success('All notifications marked as read.')
    } catch (error) {
      toast.error('Failed to mark all notifications as read.')
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
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft flex items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg">
          <Bell className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Notifications</h1>
          <p className="text-muted-foreground mt-1">Stay updated with your tasks and client interactions</p>
        </div>
      </div>

      <div className="glass bg-card/60 rounded-lg border shadow-soft p-6">
        <div className="flex justify-end mb-4">
          <Button variant="outline" onClick={handleMarkAllRead} disabled={notifications.every(n => n.read)}>
            Mark All as Read
          </Button>
        </div>
        {notifications.length > 0 ? (
          <div className="space-y-4">
            {notifications.map((notification: any) => (
              <div
                key={notification.id}
                className={cn(
                  "p-4 rounded-lg shadow-sm transition-all",
                  notification.read ? 'bg-background/30 text-muted-foreground' : 'bg-background/50 text-foreground hover:bg-background/70'
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">{notification.title}</p>
                    <p className="text-sm mt-1">{notification.message}</p>
                    <p className="text-xs mt-2 opacity-75">{new Date(notification.createdAt).toLocaleString()}</p>
                  </div>
                  {!notification.read && (
                    <Button variant="ghost" size="sm" onClick={() => handleMarkRead(notification.id)}>
                      Mark as Read
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-8">No new notifications.</p>
        )}
      </div>
      </div>
    </div>
  )
}
