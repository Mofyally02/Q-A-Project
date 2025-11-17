import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { User, UserRole, LoginResponse } from '@/types'
import { api } from '@/lib/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Computed
  userRole: UserRole | null
  userName: string
  userInitials: string
  
  // Actions
  login: (email: string, password: string) => Promise<LoginResponse>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  hasRole: (role: UserRole) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get): AuthState => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      
      get userRole() {
        return get().user?.role || null
      },
      
      get userName() {
        const user = get().user
        return user ? `${user.first_name} ${user.last_name}` : 'Guest'
      },
      
      get userInitials() {
        const user = get().user
        if (!user) return 'G'
        return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
      },
      
      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post<LoginResponse>('/auth/login', {
            email,
            password
          })
          
          if (response.data.success && response.data.access_token && response.data.user) {
            set({
              user: response.data.user,
              token: response.data.access_token,
              isAuthenticated: true,
              isLoading: false
            })
            
            // Set token in axios default headers
            api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
            
            return response.data
          }
          
          set({ isLoading: false })
          return response.data
        } catch (error: any) {
          set({ isLoading: false })
          return {
            success: false,
            message: error.response?.data?.detail || 'Login failed'
          }
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        })
        
        // Remove token from axios headers
        delete api.defaults.headers.common['Authorization']
        
        // Clear localStorage
        localStorage.removeItem('auth-storage')
      },
      
      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user })
      },
      
      setToken: (token: string | null) => {
        set({ token })
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        } else {
          delete api.defaults.headers.common['Authorization']
        }
      },
      
      hasRole: (role: UserRole) => {
        return get().user?.role === role
      }
    }),
    {
      name: 'auth-storage',
      storage: typeof window !== 'undefined' ? createJSONStorage(() => localStorage) : undefined,
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

