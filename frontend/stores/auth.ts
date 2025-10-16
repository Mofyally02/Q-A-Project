import { defineStore } from 'pinia'
import { type User, UserRole } from '~/types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    isLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user && !!state.token,
    userRole: (state) => state.user?.role || null,
    userName: (state) => state.user?.name || '',
    userEmail: (state) => state.user?.email || '',
    userAvatar: (state) => state.user?.avatar || '',
    userInitials: (state) => {
      const name = state.user?.name || ''
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2)
    }
  },

  actions: {
    async login(email: string, password: string) {
      this.isLoading = true
      try {
        const api = useApi()
        const response = await api.login(email, password)
        
        if (response.success) {
          this.user = response.user
          this.token = response.access_token
          
          // Store in localStorage
          if (process.client) {
            localStorage.setItem('auth_token', this.token)
            localStorage.setItem('user_data', JSON.stringify(this.user))
          }
        } else {
          throw new Error(response.message || 'Login failed')
        }
      } catch (error) {
        console.error('Login error:', error)
        throw new Error('Login failed. Please check your credentials.')
      } finally {
        this.isLoading = false
      }
    },

    async register(email: string, password: string, name: string, role: UserRole) {
      this.isLoading = true
      try {
        const api = useApi()
        
        // Split name into first and last name
        const nameParts = name.trim().split(' ')
        const firstName = nameParts[0] || ''
        const lastName = nameParts.slice(1).join(' ') || ''
        
        const payload = { email, password, first_name: firstName, last_name: lastName }
        const response = role === 'client'
          ? await api.registerClient(payload)
          : role === 'expert'
            ? await api.registerExpert(payload)
            : await api.register({ ...payload, role })
        
        if (response.success) {
          this.user = response.user
          this.token = response.access_token
          
          // Store in localStorage
          if (process.client) {
            localStorage.setItem('auth_token', this.token)
            localStorage.setItem('user_data', JSON.stringify(this.user))
          }
        } else {
          throw new Error(response.message || 'Registration failed')
        }
      } catch (error) {
        console.error('Registration error:', error)
        throw new Error('Registration failed. Please try again.')
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      this.user = null
      this.token = null
      
      if (process.client) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
      }
    },

    async initializeAuth() {
      if (process.client) {
        const token = localStorage.getItem('auth_token')
        const userData = localStorage.getItem('user_data')
        
        if (token && userData) {
          try {
            this.token = token
            this.user = JSON.parse(userData)
          } catch (error) {
            console.error('Failed to parse user data:', error)
            await this.logout()
          }
        }
      }
    },

    hasRole(role: UserRole | string): boolean {
      return this.user?.role === role
    }
  }
})