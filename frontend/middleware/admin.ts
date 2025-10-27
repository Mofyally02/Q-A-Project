export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return navigateTo('/auth/login')
  }
  
  if (!authStore.hasRole('admin')) {
    return navigateTo('/dashboard')
  }
})
