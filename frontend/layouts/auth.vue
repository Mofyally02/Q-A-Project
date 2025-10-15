<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
          <Icon name="heroicons:academic-cap" class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">
          AL-Tech Academy
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          AI-Powered Q&A System
        </p>
      </div>
      
      <!-- Auth Form -->
      <div class="bg-white rounded-xl shadow-soft p-8">
        <slot />
      </div>
      
      <!-- Footer -->
      <div class="text-center">
        <p class="text-xs text-gray-500">
          © 2024 AL-Tech Academy. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Auth layout meta
definePageMeta({
  layout: false
})
</script>
