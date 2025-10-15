<template>
  <nav class="bg-white shadow-soft border-b border-gray-200 fixed w-full top-0 z-30">
    <div class="container-custom">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center space-x-4">
          <NuxtLink to="/" class="flex items-center space-x-2">
            <div class="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Icon name="heroicons:academic-cap" class="h-5 w-5 text-white" />
            </div>
            <span class="text-xl font-bold text-gray-900">AL-Tech Academy</span>
          </NuxtLink>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <NuxtLink 
            v-for="item in navigationItems" 
            :key="item.name"
            :to="item.href"
            class="text-gray-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            :class="{ 'text-primary-600 bg-primary-50': isActiveRoute(item.href) }"
          >
            {{ item.name }}
          </NuxtLink>
        </div>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <!-- Notifications -->
          <button 
            @click="toggleNotifications"
            class="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors duration-200 relative"
          >
            <Icon name="heroicons:bell" class="h-5 w-5" />
            <span 
              v-if="unreadNotifications > 0"
              class="absolute -top-1 -right-1 h-4 w-4 bg-error-500 text-white text-xs rounded-full flex items-center justify-center"
            >
              {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
            </span>
          </button>

          <!-- User Dropdown -->
          <div class="relative" ref="userMenuRef">
            <button 
              @click="toggleUserMenu"
              class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              <div class="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-white">
                  {{ userInitials }}
                </span>
              </div>
              <span class="hidden md:block text-sm font-medium text-gray-700">
                {{ authStore.userName }}
              </span>
              <Icon name="heroicons:chevron-down" class="h-4 w-4 text-gray-500" />
            </button>

            <!-- Dropdown Menu -->
            <div 
              v-if="isUserMenuOpen"
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-hard border border-gray-200 py-1 z-50"
            >
              <NuxtLink 
                to="/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                @click="closeUserMenu"
              >
                Profile
              </NuxtLink>
              <NuxtLink 
                to="/settings"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                @click="closeUserMenu"
              >
                Settings
              </NuxtLink>
              <hr class="my-1 border-gray-200">
              <button 
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Sign out
              </button>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button 
            @click="toggleMobileMenu"
            class="md:hidden p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors duration-200"
          >
            <Icon name="heroicons:bars-3" class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="isMobileMenuOpen" class="md:hidden border-t border-gray-200 py-4">
        <div class="space-y-2">
          <NuxtLink 
            v-for="item in navigationItems" 
            :key="item.name"
            :to="item.href"
            class="block px-3 py-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-md text-sm font-medium transition-colors duration-200"
            :class="{ 'text-primary-600 bg-primary-50': isActiveRoute(item.href) }"
            @click="closeMobileMenu"
          >
            {{ item.name }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useUIStore } from '~/stores/ui'
import { UserRole } from '~/types'

const authStore = useAuthStore()
const uiStore = useUIStore()
const router = useRouter()
const route = useRoute()

// Reactive state
const isUserMenuOpen = ref(false)
const isMobileMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement>()

// Computed properties
const userInitials = computed(() => {
  const name = authStore.userName
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const unreadNotifications = computed(() => {
  // This would come from a notifications store
  return 0
})

const navigationItems = computed(() => {
  const items = [
    { name: 'Home', href: '/', roles: [UserRole.CLIENT, UserRole.EXPERT, UserRole.ADMIN] },
    { name: 'Questions', href: '/questions', roles: [UserRole.CLIENT, UserRole.EXPERT, UserRole.ADMIN] },
    { name: 'Ask Question', href: '/ask', roles: [UserRole.CLIENT] },
    { name: 'Reviews', href: '/reviews', roles: [UserRole.EXPERT] },
    { name: 'Analytics', href: '/admin/analytics', roles: [UserRole.ADMIN] },
    { name: 'Users', href: '/admin/users', roles: [UserRole.ADMIN] }
  ]

  return items.filter(item => 
    !authStore.user?.role || item.roles.includes(authStore.user.role)
  )
})

// Methods
const isActiveRoute = (href: string) => {
  return route.path === href
}

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const closeUserMenu = () => {
  isUserMenuOpen.value = false
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const toggleNotifications = () => {
  uiStore.toggleNotifications()
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    closeUserMenu()
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Close menus when clicking outside
onClickOutside(userMenuRef, () => {
  isUserMenuOpen.value = false
})

// Close mobile menu on route change
watch(() => route.path, () => {
  closeMobileMenu()
})
</script>
