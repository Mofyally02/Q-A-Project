<template>
  <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
    <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
      <!-- Logo -->
      <div class="flex h-16 shrink-0 items-center">
        <NuxtLink to="/" class="flex items-center space-x-2">
          <div class="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Icon name="heroicons:academic-cap" class="h-5 w-5 text-white" />
          </div>
          <span class="text-xl font-bold text-gray-900">AL-Tech Academy</span>
        </NuxtLink>
      </div>

      <!-- Navigation -->
      <nav class="flex flex-1 flex-col">
        <ul role="list" class="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" class="-mx-2 space-y-1">
              <li v-for="item in navigationItems" :key="item.name">
                <NuxtLink 
                  :to="item.href"
                  class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors duration-200"
                  :class="[
                    isActiveRoute(item.href) 
                      ? 'bg-primary-50 text-primary-600' 
                      : 'text-gray-700 hover:text-primary-600 hover:bg-primary-50'
                  ]"
                >
                  <Icon 
                    :name="item.icon" 
                    class="h-6 w-6 shrink-0"
                    :class="[
                      isActiveRoute(item.href) 
                        ? 'text-primary-600' 
                        : 'text-gray-400 group-hover:text-primary-600'
                    ]"
                  />
                  {{ item.name }}
                </NuxtLink>
              </li>
            </ul>
          </li>

          <!-- User Section -->
          <li class="mt-auto">
            <div class="border-t border-gray-200 pt-4">
              <div class="flex items-center space-x-3 px-2">
                <div class="h-10 w-10 bg-primary-600 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-white">
                    {{ userInitials }}
                  </span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ authStore.userName }}
                  </p>
                  <p class="text-xs text-gray-500 truncate">
                    {{ authStore.userEmail }}
                  </p>
                </div>
              </div>
              
              <div class="mt-3 space-y-1">
                <NuxtLink 
                  to="/profile"
                  class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-primary-50 transition-colors duration-200"
                >
                  <Icon name="heroicons:user" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-primary-600" />
                  Profile
                </NuxtLink>
                <NuxtLink 
                  to="/settings"
                  class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-primary-50 transition-colors duration-200"
                >
                  <Icon name="heroicons:cog-6-tooth" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-primary-600" />
                  Settings
                </NuxtLink>
                <button 
                  @click="handleLogout"
                  class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-error-600 hover:bg-error-50 transition-colors duration-200 w-full text-left"
                >
                  <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-error-600" />
                  Sign out
                </button>
              </div>
            </div>
          </li>
        </ul>
      </nav>
    </div>
  </div>

  <!-- Mobile Sidebar -->
  <div 
    v-if="isSidebarOpen"
    class="fixed inset-0 z-50 lg:hidden"
  >
    <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200">
      <div class="flex h-full flex-col">
        <!-- Mobile Header -->
        <div class="flex h-16 shrink-0 items-center justify-between px-6 border-b border-gray-200">
          <div class="flex items-center space-x-2">
            <div class="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Icon name="heroicons:academic-cap" class="h-5 w-5 text-white" />
            </div>
            <span class="text-xl font-bold text-gray-900">AL-Tech Academy</span>
          </div>
          <button 
            @click="toggleSidebar"
            class="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors duration-200"
          >
            <Icon name="heroicons:x-mark" class="h-5 w-5" />
          </button>
        </div>

        <!-- Mobile Navigation -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <nav class="flex flex-col space-y-4">
            <NuxtLink 
              v-for="item in navigationItems" 
              :key="item.name"
              :to="item.href"
              class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors duration-200"
              :class="[
                isActiveRoute(item.href) 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:text-primary-600 hover:bg-primary-50'
              ]"
              @click="toggleSidebar"
            >
              <Icon 
                :name="item.icon" 
                class="h-6 w-6 shrink-0"
                :class="[
                  isActiveRoute(item.href) 
                    ? 'text-primary-600' 
                    : 'text-gray-400 group-hover:text-primary-600'
                ]"
              />
              {{ item.name }}
            </NuxtLink>
          </nav>
        </div>

        <!-- Mobile User Section -->
        <div class="border-t border-gray-200 p-6">
          <div class="flex items-center space-x-3 mb-4">
            <div class="h-10 w-10 bg-primary-600 rounded-full flex items-center justify-center">
              <span class="text-sm font-medium text-white">
                {{ userInitials }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ authStore.userName }}
              </p>
              <p class="text-xs text-gray-500 truncate">
                {{ authStore.userEmail }}
              </p>
            </div>
          </div>
          
          <div class="space-y-2">
            <NuxtLink 
              to="/profile"
              class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-primary-50 transition-colors duration-200"
              @click="toggleSidebar"
            >
              <Icon name="heroicons:user" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-primary-600" />
              Profile
            </NuxtLink>
            <NuxtLink 
              to="/settings"
              class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-primary-50 transition-colors duration-200"
              @click="toggleSidebar"
            >
              <Icon name="heroicons:cog-6-tooth" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-primary-600" />
              Settings
            </NuxtLink>
            <button 
              @click="handleLogout"
              class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-error-600 hover:bg-error-50 transition-colors duration-200 w-full text-left"
            >
              <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5 shrink-0 text-gray-400 group-hover:text-error-600" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useUIStore } from '~/stores/ui'
import { UserRole } from '~/types'

const authStore = useAuthStore()
const uiStore = useUIStore()
const route = useRoute()

// Reactive state
const { isSidebarOpen } = storeToRefs(uiStore)

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

const navigationItems = computed(() => {
  const items = [
    { 
      name: 'Dashboard', 
      href: '/dashboard', 
      icon: 'heroicons:home',
      roles: [UserRole.CLIENT, UserRole.EXPERT, UserRole.ADMIN] 
    },
    { 
      name: 'Questions', 
      href: '/questions', 
      icon: 'heroicons:chat-bubble-left-right',
      roles: [UserRole.CLIENT, UserRole.EXPERT, UserRole.ADMIN] 
    },
    { 
      name: 'Ask Question', 
      href: '/ask', 
      icon: 'heroicons:plus-circle',
      roles: [UserRole.CLIENT] 
    },
    { 
      name: 'My Reviews', 
      href: '/reviews', 
      icon: 'heroicons:clipboard-document-check',
      roles: [UserRole.EXPERT] 
    },
    { 
      name: 'Pending Reviews', 
      href: '/reviews/pending', 
      icon: 'heroicons:clock',
      roles: [UserRole.EXPERT] 
    },
    { 
      name: 'Analytics', 
      href: '/admin/analytics', 
      icon: 'heroicons:chart-bar',
      roles: [UserRole.ADMIN] 
    },
    { 
      name: 'Users', 
      href: '/admin/users', 
      icon: 'heroicons:users',
      roles: [UserRole.ADMIN] 
    },
    { 
      name: 'System', 
      href: '/admin/system', 
      icon: 'heroicons:cog-6-tooth',
      roles: [UserRole.ADMIN] 
    }
  ]

  return items.filter(item => 
    !authStore.user?.role || item.roles.includes(authStore.user.role)
  )
})

// Methods
const isActiveRoute = (href: string) => {
  return route.path.startsWith(href)
}

const toggleSidebar = () => {
  uiStore.toggleSidebar()
}

const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>
