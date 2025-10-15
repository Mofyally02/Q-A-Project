<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <AppSidebar />
    
    <!-- Main Content Area -->
    <div class="lg:pl-64">
      <!-- Top Navigation -->
      <AppTopNav />
      
      <!-- Page Content -->
      <main class="py-6">
        <div class="container-custom">
          <slot />
        </div>
      </main>
    </div>
    
    <!-- Mobile Sidebar Overlay -->
    <div 
      v-if="isSidebarOpen" 
      class="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
      @click="toggleSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '~/stores/ui'

const uiStore = useUIStore()
const { isSidebarOpen } = storeToRefs(uiStore)

const toggleSidebar = () => {
  uiStore.toggleSidebar()
}

// Dashboard layout meta
definePageMeta({
  layout: false
})
</script>
