/**
 * Middleware to redirect authenticated users to their role-specific dashboards
 * Used on index page and general routes
 */
export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  // Only redirect if authenticated
  if (authStore.isAuthenticated && authStore.user) {
    const role = authStore.userRole
    
    // If on root or index, redirect based on role
    if (to.path === '/' || to.path === '/index') {
      if (role === 'admin') {
        return navigateTo('/admin/dashboard')
      } else if (role === 'expert') {
        return navigateTo('/reviews')
      } else if (role === 'client') {
        return navigateTo('/questions')
      }
    }
  }
})

