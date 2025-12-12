import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { User, LoginResponse } from '@/types'
import { UserRole } from '@/types'


interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  isHydrated: boolean // Track if store has been hydrated from storage
  
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
  hydrate: () => void // Manually trigger hydration
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get): AuthState => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      isHydrated: false,
      
      get userRole() {
        try {
          const state = get()
          return state?.user?.role || null
        } catch {
          return null
        }
      },
      
      get userName() {
        try {
          const state = get()
          const user = state?.user
        return user ? `${user.first_name} ${user.last_name}` : 'Guest'
        } catch {
          return 'Guest'
        }
      },
      
      get userInitials() {
        try {
          const state = get()
          const user = state?.user
        if (!user) return 'G'
        return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
        } catch {
          return 'G'
        }
      },
      
      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          // Lazy load API to avoid circular dependency
          const api = await import('@/app/client/lib/api').then(m => m.api)
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
        
        // Remove token from axios headers (lazy load to avoid circular dependency)
        if (typeof window !== 'undefined') {
          import('@/app/client/lib/api').then((module) => {
            delete module.api.defaults.headers.common['Authorization']
          })
        }
        
        // Clear localStorage
        localStorage.removeItem('auth-storage')
      },
      
      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user })
      },
      
      setToken: (token: string | null) => {
        set({ token })
        // Set token in axios headers (lazy load to avoid circular dependency)
        if (typeof window !== 'undefined') {
          import('@/app/client/lib/api').then((module) => {
        if (token) {
              module.api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        } else {
              delete module.api.defaults.headers.common['Authorization']
            }
          })
        }
      },
      
      hasRole: (role: UserRole) => {
        const state = get()
        return state?.user?.role === role
      },
      
      hydrate: () => {
        // This will be called after persist middleware hydrates
        const state = get()
        if (state.token && typeof window !== 'undefined') {
          // Set token in axios headers when hydrating (lazy load to avoid circular dependency)
          import('@/app/client/lib/api').then((module) => {
            module.api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
          })
        }
        set({ isHydrated: true })
      }
    }),
    {
      name: 'auth-storage',
      storage: typeof window !== 'undefined' ? createJSONStorage(() => localStorage) : undefined,
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      }),
      onRehydrateStorage: () => (state, error) => {
        // Called after rehydration completes
        if (error) {
          console.error('Failed to rehydrate auth store:', error)
          return
        }
        
        if (state && typeof window !== 'undefined') {
          // Set token in axios headers (lazy load to avoid circular dependency)
          if (state.token) {
            import('@/app/client/lib/api').then((module) => {
              module.api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
            })
          }
          // Mark as hydrated using set() to properly update state
          setTimeout(() => {
            useAuthStore.setState({ isHydrated: true })
          }, 0)
        }
      }
    }
  )
)

// Auto-hydrate on mount (client-side only)
if (typeof window !== 'undefined') {
  // Wait for next tick to ensure store is ready
  setTimeout(() => {
    const state = useAuthStore.getState()
    if (!state.isHydrated) {
      useAuthStore.getState().hydrate()
    }
  }, 0)
}

