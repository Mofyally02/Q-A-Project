
'use client'

import { Settings, Loader2, Moon, Sun, CheckCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { useTheme } from 'next-themes'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { Button } from '@/app/client/components/ui/button'

export default function ExpertSettingsPage() {
  const router = useRouter()
  const { setTheme, theme } = useTheme()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [profileForm, setProfileForm] = useState({
    firstName: 'Jane', // Mock data
    lastName: 'Doe',    // Mock data
    email: 'jane.doe@example.com', // Mock data
    specialization: 'Mathematics'
  })

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getExpertProfile: async () => { // Assuming an endpoint for expert profile
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                firstName: 'Jane',
                lastName: 'Doe',
                email: 'jane.doe@example.com',
                specialization: 'Mathematics'
              }
            }
          })
        }, 500)
      })
    },
    updateExpertProfile: async (data: any) => { // Assuming an endpoint for profile update
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    data: {
                        success: true,
                        message: 'Profile updated successfully!'
                    }
                })
            }, 500)
        })
    }
  }

  useEffect(() => {
    // if (!user || user.role !== UserRole.EXPERT) {
    //   router.push('/login')
    //   toast.error('Expert access only.')
    //   return
    // }

    const fetchProfile = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getExpertProfile()
        if (response.data.success) {
          setProfileForm(response.data.data)
        } else {
          toast.error(response.data.message || 'Failed to load profile.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching profile data.')
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [])

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response: any = await apiHelpers.updateExpertProfile(profileForm)
      if (response.data.success) {
        toast.success(response.data.message)
      } else {
        toast.error(response.data.message || 'Failed to update profile.')
      }
    } catch (error) {
      toast.error('An error occurred while updating profile.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft flex items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg">
          <Settings className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage your profile and preferences</p>
        </div>
      </div>

      {/* Profile Settings */}
      <div className="glass bg-card/60 rounded-lg border shadow-soft p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Profile Information</h2>
        <form onSubmit={handleProfileSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-foreground mb-2">
                First Name
              </label>
              <input
                type="text"
                id="firstName"
                value={profileForm.firstName}
                onChange={(e) => setProfileForm({ ...profileForm, firstName: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-foreground mb-2">
                Last Name
              </label>
              <input
                type="text"
                id="lastName"
                value={profileForm.lastName}
                onChange={(e) => setProfileForm({ ...profileForm, lastName: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={profileForm.email}
              disabled
              className="w-full px-4 py-2 border border-border rounded-lg bg-background/30 cursor-not-allowed"
            />
          </div>
          <div>
            <label htmlFor="specialization" className="block text-sm font-medium text-foreground mb-2">
                Specialization
            </label>
            <input
                type="text"
                id="specialization"
                value={profileForm.specialization}
                onChange={(e) => setProfileForm({ ...profileForm, specialization: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background/50 focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4 mr-2" />}
            Save Profile
          </Button>
        </form>
      </div>

      {/* Theme Settings */}
      <div className="glass bg-card/60 rounded-lg border shadow-soft p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Theme</h2>
        <div className="flex items-center space-x-4">
          <Button
            variant={theme === 'light' ? 'default' : 'outline'}
            onClick={() => setTheme('light')}
          >
            <Sun className="h-4 w-4 mr-2" /> Light
          </Button>
          <Button
            variant={theme === 'dark' ? 'default' : 'outline'}
            onClick={() => setTheme('dark')}
          >
            <Moon className="h-4 w-4 mr-2" /> Dark
          </Button>
        </div>
      </div>

      {/* Other Settings Placeholder */}
      <div className="glass bg-card/60 rounded-lg border shadow-soft p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Other Settings</h2>
        <p className="text-muted-foreground">More settings options coming soon...</p>
      </div>
      </div>
    </div>
  )
}
