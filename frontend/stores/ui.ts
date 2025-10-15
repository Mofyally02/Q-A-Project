import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', () => {
  // State
  const isSidebarOpen = ref(false)
  const isNotificationsOpen = ref(false)
  const isDarkMode = ref(false)
  const isLoading = ref(false)
  const loadingMessage = ref('')

  // Actions
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  const openSidebar = () => {
    isSidebarOpen.value = true
  }

  const closeSidebar = () => {
    isSidebarOpen.value = false
  }

  const toggleNotifications = () => {
    isNotificationsOpen.value = !isNotificationsOpen.value
  }

  const closeNotifications = () => {
    isNotificationsOpen.value = false
  }

  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    
    // Apply dark mode to document
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    
    // Save to localStorage
    localStorage.setItem('darkMode', isDarkMode.value.toString())
  }

  const setLoading = (loading: boolean, message = '') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  const showLoading = (message = 'Loading...') => {
    setLoading(true, message)
  }

  const hideLoading = () => {
    setLoading(false, '')
  }

  const initializeUI = () => {
    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode')
    if (savedDarkMode !== null) {
      isDarkMode.value = savedDarkMode === 'true'
      if (isDarkMode.value) {
        document.documentElement.classList.add('dark')
      }
    }

    // Close sidebar on mobile by default
    if (window.innerWidth < 1024) {
      isSidebarOpen.value = false
    }
  }

  // Computed
  const isMobile = computed(() => {
    if (process.client) {
      return window.innerWidth < 768
    }
    return false
  })

  const isTablet = computed(() => {
    if (process.client) {
      return window.innerWidth >= 768 && window.innerWidth < 1024
    }
    return false
  })

  const isDesktop = computed(() => {
    if (process.client) {
      return window.innerWidth >= 1024
    }
    return false
  })

  return {
    // State
    isSidebarOpen: readonly(isSidebarOpen),
    isNotificationsOpen: readonly(isNotificationsOpen),
    isDarkMode: readonly(isDarkMode),
    isLoading: readonly(isLoading),
    loadingMessage: readonly(loadingMessage),
    
    // Computed
    isMobile,
    isTablet,
    isDesktop,
    
    // Actions
    toggleSidebar,
    openSidebar,
    closeSidebar,
    toggleNotifications,
    closeNotifications,
    toggleDarkMode,
    setLoading,
    showLoading,
    hideLoading,
    initializeUI
  }
})
