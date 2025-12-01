'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { LogIn, UserPlus, Mail, Lock, User } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/app/client/lib/api'

export default function AuthPage() {
  const router = useRouter()
  const { login, isLoading } = useAuthStore()
  const [isLogin, setIsLogin] = useState(true)
  
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  })
  
  const [signupForm, setSignupForm] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: ''
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const response = await login(loginForm.email, loginForm.password)
      
      if (response.success) {
        // Redirect based on role
        const userRole = response.user?.role
        if (!userRole) {
          router.push('/client/dashboard')
          return
        }
        
        // Handle both enum values and string values from backend
        // Convert to string for comparison
        const roleString = typeof userRole === 'string' ? userRole : String(userRole)
        
        // Super admin always defaults to admin dashboard, but can access all routes
        if (roleString === UserRole.SUPER_ADMIN || roleString === 'super_admin' || 
            response.user?.email === 'allansaiti02@gmail.com') {
          router.push('/admin/dashboard')
        } else if (roleString === UserRole.ADMIN || roleString === UserRole.ADMIN_EDITOR || 
                   roleString === 'admin' || roleString === 'admin_editor') {
          router.push('/admin/dashboard')
        } else if (roleString === UserRole.EXPERT || roleString === 'expert') {
          router.push('/expert/tasks')
        } else {
          router.push('/client/dashboard')
        }
      } else {
        toast.error(response.message || 'Login failed')
      }
    } catch (error: any) {
      toast.error(error.message || 'Login failed')
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate password length
    if (signupForm.password.length < 8) {
      toast.error('Password must be at least 8 characters long')
      return
    }
    
    // Validate required fields
    if (!signupForm.firstName || !signupForm.lastName || !signupForm.email) {
      toast.error('Please fill in all required fields')
      return
    }
    
    try {
      const response = await api.post('/auth/register', {
        email: signupForm.email,
        password: signupForm.password,
        first_name: signupForm.firstName,
        last_name: signupForm.lastName,
        role: 'client' // Always assign client role for new signups
      })
      
      if (response.data?.success) {
        toast.success('Account created successfully!')
        
        // Auto-login after signup using the token from registration
        if (response.data?.access_token && response.data?.user) {
          // Store token and user data directly
          const { setUser, setToken } = useAuthStore.getState()
          setUser(response.data.user)
          setToken(response.data.access_token)
          
          // Always redirect to client dashboard for new signups
          router.push('/client/dashboard')
        } else {
          // Fallback: try login
          const loginResponse = await login(signupForm.email, signupForm.password)
          if (loginResponse.success) {
            router.push('/client/dashboard')
          } else {
            toast.error('Account created but login failed. Please try logging in.')
          }
        }
      } else {
        toast.error(response.data?.message || 'Registration failed')
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Registration failed'
      toast.error(errorMessage)
      console.error('Registration error:', error)
    }
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4 sm:p-6 safe-top safe-bottom">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-lg shadow-xl p-6 sm:p-8 lg:p-10 animate-scale-in">
          {/* Logo */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="w-14 h-14 sm:w-16 sm:h-16 lg:w-20 lg:h-20 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-lg sm:rounded-lg flex items-center justify-center mx-auto mb-3 sm:mb-4 shadow-lg border-2 border-teal-300 dark:border-teal-600">
              <User className="w-7 h-7 sm:w-8 sm:h-8 lg:w-10 lg:h-10 text-white" />
            </div>
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">AL-Tech Writers</h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">Academic Assignment Writers</p>
          </div>

          {/* Toggle Login/Signup */}
          <div className="flex gap-2 mb-4 sm:mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 sm:py-3 px-4 rounded-lg font-medium transition-all duration-200 active:scale-95 ${
                isLogin
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <LogIn className="w-4 h-4 sm:w-5 sm:h-5 inline mr-2" />
              <span className="hidden sm:inline">Sign In</span>
              <span className="sm:hidden">Login</span>
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 sm:py-3 px-4 rounded-lg font-medium transition-all duration-200 active:scale-95 ${
                !isLogin
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <UserPlus className="w-4 h-4 sm:w-5 sm:h-5 inline mr-2" />
              <span className="hidden sm:inline">Sign Up</span>
              <span className="sm:hidden">Signup</span>
            </button>
          </div>

          {/* Login Form */}
          {isLogin ? (
            <form onSubmit={handleLogin} className="space-y-3 sm:space-y-4">
              <div>
                <label className="block text-sm sm:text-base font-medium text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                  <input
                    type="email"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                    required
                    className="w-full pl-10 pr-4 py-2.5 sm:py-3 border border-input rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground placeholder:text-muted-foreground transition-all duration-200"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm sm:text-base font-medium text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                  <input
                    type="password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    required
                    className="w-full pl-10 pr-4 py-2.5 sm:py-3 border border-input rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground placeholder:text-muted-foreground transition-all duration-200"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary mt-4 sm:mt-6"
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={signupForm.firstName}
                    onChange={(e) => setSignupForm({ ...signupForm, firstName: e.target.value })}
                    required
                    className="w-full input-primary"
                    placeholder="First name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={signupForm.lastName}
                    onChange={(e) => setSignupForm({ ...signupForm, lastName: e.target.value })}
                    required
                    className="w-full input-primary"
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={signupForm.email}
                  onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                  required
                  className="w-full input-primary"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={signupForm.password}
                  onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
                  required
                  minLength={8}
                  className="w-full input-primary"
                  placeholder="At least 8 characters"
                />
              </div>

              <button
                type="submit"
                className="w-full btn-primary"
              >
                Create Account
              </button>
            </form>
          )}

          {/* Sign up / Forgot Password Links */}
          {isLogin && (
            <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-border flex items-center justify-between text-sm">
              <button
                onClick={() => setIsLogin(false)}
                className="text-primary hover:text-primary/80 font-medium transition-colors"
              >
                Don't have an account? <span className="text-warning">Sign up</span>
              </button>
              <button
                className="text-warning hover:text-warning/80 font-medium transition-colors"
              >
                Forgot Password?
              </button>
            </div>
          )}
          
          {!isLogin && (
            <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-border text-center text-sm">
              <button
                onClick={() => setIsLogin(true)}
                className="text-primary hover:text-primary/80 font-medium transition-colors"
              >
                Already have an account? <span className="text-warning">Sign in</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

