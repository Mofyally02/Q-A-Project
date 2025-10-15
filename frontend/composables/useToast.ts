export const useToast = () => {
  const show = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    if (process.client) {
      // Create toast element
      const toast = document.createElement('div')
      toast.className = `toast toast-${type} animate-fade-in`
      
      const iconMap = {
        success: '✅',
        error: '❌', 
        info: 'ℹ️',
        warning: '⚠️'
      }
      
      toast.innerHTML = `
        <div class="flex items-center space-x-2">
          <span>${iconMap[type]}</span>
          <span class="text-sm font-medium">${message}</span>
        </div>
      `
      
      // Get or create toast container
      let container = document.getElementById('toast-container')
      if (!container) {
        container = document.createElement('div')
        container.id = 'toast-container'
        container.className = 'fixed top-4 right-4 z-50 space-y-2'
        document.body.appendChild(container)
      }
      
      container.appendChild(toast)
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast)
        }
      }, 5000)
      
      // Remove on click
      toast.addEventListener('click', () => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast)
        }
      })
    }
  }
  
  return {
    success: (message: string) => show(message, 'success'),
    error: (message: string) => show(message, 'error'),
    info: (message: string) => show(message, 'info'),
    warning: (message: string) => show(message, 'warning')
  }
}

