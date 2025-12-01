'use client'

import { Bell, Loader2, CheckCircle2, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function ClientNotificationsPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [notifications, setNotifications] = useState<any[]>([])

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only')
      return
    }
    loadNotifications()
  }, [user, isAuthenticated, router])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const response: any = await apiHelpers.getNotifications()
      const data = response.data?.data || response.data
      setNotifications(data?.notifications || [])
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await apiHelpers.markNotificationRead(notificationId)
      setNotifications(notifications.map(n => 
        n.id === notificationId || n.notification_id === notificationId 
          ? { ...n, read: true } 
          : n
      ))
    } catch (error: any) {
      toast.error('Failed to mark notification as read')
    }
  }

  const markAllAsRead = async () => {
    try {
      await apiHelpers.markAllNotificationsRead()
      setNotifications(notifications.map(n => ({ ...n, read: true })))
      toast.success('All notifications marked as read')
    } catch (error: any) {
      toast.error('Failed to mark all as read')
    }
  }

  if (loading && notifications.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Notifications</h1>
          <p className="text-muted-foreground mt-1">Stay updated with your questions and answers</p>
        </div>
        {unreadCount > 0 && (
          <Button variant="outline" onClick={markAllAsRead}>
            Mark all as read
          </Button>
        )}
      </div>

      {/* Notifications List */}
      <Card className="p-6">
        {notifications.length > 0 ? (
          <div className="space-y-4">
            {notifications.map((notification) => (
              <div
                key={notification.id || notification.notification_id}
                className={`p-4 rounded-lg border transition-colors ${
                  notification.read 
                    ? 'bg-background border-border' 
                    : 'bg-primary/5 border-primary/20'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-foreground">
                        {notification.title || notification.subject}
                      </h3>
                      {!notification.read && (
                        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                          New
                        </Badge>
                      )}
                    </div>
                    <p className="text-muted-foreground text-sm mb-2">
                      {notification.message || notification.body}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(notification.created_at || notification.sent_at).toLocaleString()}
                    </p>
                  </div>
                  {!notification.read && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => markAsRead(notification.id || notification.notification_id)}
                    >
                      <CheckCircle2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">No notifications</p>
          </div>
        )}
      </Card>
    </div>
  )
}
