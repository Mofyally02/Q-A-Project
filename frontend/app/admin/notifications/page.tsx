'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  BellRing, 
  Loader2, 
  Plus,
  X,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Calendar
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
import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/client/components/ui/dropdown-menu'

export default function AdminNotificationsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [notifications, setNotifications] = useState<any[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [notificationForm, setNotificationForm] = useState({
    title: '',
    type: 'info',
    message: '',
    priority: 'medium',
    expires_at: '',
    target_roles: ['client'] as string[], // Default to clients
    send_email: false,
    send_sms: false
  })
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
    loadNotifications()
  }, [user, router])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const response = await apiHelpers.getAdminNotifications({ page_size: 100 })
      // Backend returns { broadcasts: [...], total, page, page_size }
      const data = response.data?.data || response.data
      setNotifications(data?.broadcasts || data?.notifications || [])
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNotification = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // Map roles to backend format
      const targetRoles = notificationForm.target_roles.map(role => {
        if (role === 'clients') return 'client'
        if (role === 'experts') return 'expert'
        if (role === 'admins') return 'admin'
        return role
      })

      const payload = {
        title: notificationForm.title,
        message: notificationForm.message,
        notification_type: notificationForm.type,
        target_roles: targetRoles.length > 0 ? targetRoles : null,
        send_email: notificationForm.send_email,
        send_sms: notificationForm.send_sms
      }
      
      await apiHelpers.sendNotification(payload)
      toast.success('Notification created successfully')
      setIsModalOpen(false)
      setNotificationForm({
        title: '',
        type: 'info',
        message: '',
        priority: 'medium',
        expires_at: '',
        target_roles: ['client'],
        send_email: false,
        send_sms: false
      })
      await loadNotifications()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create notification')
    }
  }

  const filteredNotifications = notifications.filter(notif => {
    if (!searchQuery) return true
    return (
      notif.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notif.message?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notif.type?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  const getTypeBadgeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'info':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      case 'warning':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'error':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'success':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  const getPriorityBadgeColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'low':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  const getStatusBadge = (notif: any) => {
    // Check if notification was sent successfully
    const sentCount = notif.sent_count || 0
    const failedCount = notif.failed_count || 0
    const targetCount = notif.target_count || 0
    
    if (targetCount > 0 && sentCount === targetCount) {
      return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Delivered</Badge>
    } else if (sentCount > 0) {
      return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Partial</Badge>
    } else if (failedCount > 0) {
      return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Failed</Badge>
    }
    return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">Pending</Badge>
  }

  if (loading && notifications.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading notifications...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Notifications</h1>
          <h2 className="text-xl font-semibold text-foreground mt-2">Notification Management</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Create and manage notifications for users across all platforms.
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          className="w-full sm:w-auto"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Notification
        </Button>
      </div>

      {/* Notifications Table */}
      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Title</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Type</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Priority</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Target</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Status</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Created</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredNotifications.length > 0 ? (
                filteredNotifications.map((notif, idx) => (
                  <tr key={idx} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-foreground">{notif.title || 'No title'}</p>
                        <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                          {notif.message || 'No message'}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className={getTypeBadgeColor(notif.notification_type || notif.type || 'info')}>
                        {((notif.notification_type || notif.type || 'Info').charAt(0).toUpperCase() + (notif.notification_type || notif.type || 'Info').slice(1))}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className="bg-gray-500/10 text-gray-500 border-gray-500/20">
                        Medium
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {notif.target_roles && Array.isArray(notif.target_roles) ? (
                          notif.target_roles.map((role: string, idx: number) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {role === 'client' ? 'Clients' :
                               role === 'expert' ? 'Experts' :
                               role === 'admin' ? 'Admins' :
                               role.charAt(0).toUpperCase() + role.slice(1)}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-sm text-foreground">All Users</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(notif)}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-muted-foreground">
                        {new Date(notif.sent_at || notif.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Edit className="w-4 h-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-destructive">
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                    <BellRing className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No notifications found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Create Notification Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <Card className="w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-foreground">Create New Notification</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsModalOpen(false)}
                  className="h-8 w-8 p-0"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {/* Modal Form */}
              <form onSubmit={handleCreateNotification} className="space-y-6">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Title
                  </label>
                  <Input
                    type="text"
                    value={notificationForm.title}
                    onChange={(e) => setNotificationForm({ ...notificationForm, title: e.target.value })}
                    placeholder="Notification title"
                    className="w-full"
                    required
                  />
                </div>

                {/* Type */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Type
                  </label>
                  <select
                    value={notificationForm.type}
                    onChange={(e) => setNotificationForm({ ...notificationForm, type: e.target.value })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="success">Success</option>
                  </select>
                </div>

                {/* Message */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Message
                  </label>
                  <Textarea
                    value={notificationForm.message}
                    onChange={(e) => setNotificationForm({ ...notificationForm, message: e.target.value })}
                    placeholder="Notification message"
                    className="w-full min-h-[120px] resize-y"
                    required
                  />
                </div>

                {/* Priority */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Priority
                  </label>
                  <select
                    value={notificationForm.priority}
                    onChange={(e) => setNotificationForm({ ...notificationForm, priority: e.target.value })}
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                {/* Expires At */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Expires At (Optional)
                  </label>
                  <div className="relative">
                    <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      type="datetime-local"
                      value={notificationForm.expires_at}
                      onChange={(e) => setNotificationForm({ ...notificationForm, expires_at: e.target.value })}
                      className="w-full pr-10"
                    />
                  </div>
                </div>

                {/* Target Roles Selection */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-3">
                    Target Audience
                  </label>
                  <div className="space-y-2">
                    {['clients', 'experts', 'admins'].map((role) => (
                      <label
                        key={role}
                        className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={notificationForm.target_roles.includes(role)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNotificationForm({
                                ...notificationForm,
                                target_roles: [...notificationForm.target_roles, role]
                              })
                            } else {
                              setNotificationForm({
                                ...notificationForm,
                                target_roles: notificationForm.target_roles.filter(r => r !== role)
                              })
                            }
                          }}
                          className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                        />
                        <span className="text-sm text-foreground capitalize">
                          {role === 'admins' ? 'Admins' : role.charAt(0).toUpperCase() + role.slice(1)}
                        </span>
                      </label>
                    ))}
                  </div>
                  {notificationForm.target_roles.length === 0 && (
                    <p className="text-xs text-destructive mt-2">
                      Please select at least one target audience
                    </p>
                  )}
                </div>

                {/* Send Email Toggle */}
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Send Email
                    </label>
                    <p className="text-xs text-muted-foreground">
                      Also send notification via email
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setNotificationForm({ ...notificationForm, send_email: !notificationForm.send_email })}
                    className={cn(
                      "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                      notificationForm.send_email ? "bg-primary" : "bg-muted"
                    )}
                  >
                    <span
                      className={cn(
                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                        notificationForm.send_email ? "translate-x-6" : "translate-x-1"
                      )}
                    />
                  </button>
                </div>

                {/* Send SMS Toggle */}
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">
                      Send SMS
                    </label>
                    <p className="text-xs text-muted-foreground">
                      Also send notification via SMS
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setNotificationForm({ ...notificationForm, send_sms: !notificationForm.send_sms })}
                    className={cn(
                      "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                      notificationForm.send_sms ? "bg-primary" : "bg-muted"
                    )}
                  >
                    <span
                      className={cn(
                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                        notificationForm.send_sms ? "translate-x-6" : "translate-x-1"
                      )}
                    />
                  </button>
                </div>

                {/* Modal Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-primary hover:bg-primary/90"
                    disabled={notificationForm.target_roles.length === 0}
                  >
                    Create Notification
                  </Button>
                </div>
              </form>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
