<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow mb-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-3xl font-bold text-gray-900">System Settings</h1>
        <p class="mt-1 text-sm text-gray-500">Admin tools for system health and configuration</p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">Queue Status</h2>
          <p class="text-sm text-gray-500">Processing tasks in the system</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-2xl font-bold">—</span>
            <button class="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200">Refresh</button>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">Cache</h2>
          <p class="text-sm text-gray-500">Manage application cache</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-2xl font-bold">—</span>
            <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">Clear Cache</button>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">Database</h2>
          <p class="text-sm text-gray-500">Backups and storage</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-2xl font-bold">—</span>
            <button class="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200">Trigger Backup</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Page meta
definePageMeta({
  middleware: 'admin',
  layout: 'dashboard'
})
</script>


