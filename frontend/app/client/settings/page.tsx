'use client'

import { Settings, Loader2, Save } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

export default function ClientSettingsPage() {
  const router = useRouter()
  const { user, isAuthenticated, isHydrated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
  })

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
    loadProfile()
  }, [user, isAuthenticated, isHydrated, router])

  const loadProfile = async () => {
    try {
      setLoading(true)
      const response: any = await apiHelpers.getUserProfile()
      const data = response.data?.data || response.data
      setProfileForm({
        first_name: data?.first_name || user?.first_name || '',
        last_name: data?.last_name || user?.last_name || '',
        email: data?.email || user?.email || '',
      })
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      const response: any = await apiHelpers.updateUserProfile(profileForm)
      if (response.data?.success) {
        toast.success('Profile updated successfully')
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to update profile')
    } finally {
      setSaving(false)
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
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage your account settings and preferences</p>
        </div>
      </div>

      {/* Profile Settings */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Settings className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-semibold text-foreground">Profile Settings</h2>
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                First Name
              </label>
              <Input
                type="text"
                value={profileForm.first_name}
                onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Last Name
              </label>
              <Input
                type="text"
                value={profileForm.last_name}
                onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                className="w-full"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Email
            </label>
            <Input
              type="email"
              value={profileForm.email}
              onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
              className="w-full"
              disabled
            />
            <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
          </div>

          <div className="flex justify-end pt-4 border-t border-border">
            <Button type="submit" disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
