<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Notifications</h1>
            <p class="mt-1 text-sm text-gray-500">Send notifications to users</p>
          </div>
          <button
            @click="showSendModal = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Send Notification
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Notification History -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Notification History</h2>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div
              v-for="(notification, index) in notifications"
              :key="index"
              class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
                <p class="text-sm text-gray-500">{{ notification.message }}</p>
                <p class="text-xs text-gray-400 mt-1">Sent to: {{ notification.recipients }}</p>
              </div>
              <div class="ml-4">
                <span
                  :class="{
                    'bg-green-100 text-green-800': notification.status === 'sent',
                    'bg-yellow-100 text-yellow-800': notification.status === 'pending',
                    'bg-red-100 text-red-800': notification.status === 'failed'
                  }"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ notification.status }}
                </span>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(notification.sent_at) }}</p>
              </div>
            </div>
            <div v-if="!notifications.length" class="text-center text-gray-500 py-8">
              No notifications sent yet
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Templates -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Templates</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              @click="selectTemplate('system_maintenance')"
              class="p-4 border rounded-lg text-left hover:bg-gray-50 transition"
            >
              <h3 class="font-medium text-gray-900 mb-2">System Maintenance</h3>
              <p class="text-sm text-gray-600">Notify users about scheduled maintenance.</p>
            </button>
            <button
              @click="selectTemplate('new_feature')"
              class="p-4 border rounded-lg text-left hover:bg-gray-50 transition"
            >
              <h3 class="font-medium text-gray-900 mb-2">New Feature</h3>
              <p class="text-sm text-gray-600">Announce new features or updates.</p>
            </button>
            <button
              @click="selectTemplate('general_announcement')"
              class="p-4 border rounded-lg text-left hover:bg-gray-50 transition"
            >
              <h3 class="font-medium text-gray-900 mb-2">General Announcement</h3>
              <p class="text-sm text-gray-600">Send general announcements to users.</p>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Send Notification Modal -->
    <div
      v-if="showSendModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="showSendModal = false"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Send Notification</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input
                v-model="newNotification.title"
                type="text"
                placeholder="Notification title"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Message</label>
              <textarea
                v-model="newNotification.message"
                rows="4"
                placeholder="Notification message"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Recipients</label>
              <select
                v-model="newNotification.recipients"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Users</option>
                <option value="clients">Clients Only</option>
                <option value="experts">Experts Only</option>
                <option value="admins">Admins Only</option>
              </select>
            </div>
            <div class="flex justify-end gap-3 pt-4">
              <button
                @click="showSendModal = false"
                class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                @click="sendNotification"
                class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Page meta
definePageMeta({
  middleware: 'admin'
})

const notifications = ref([])
const showSendModal = ref(false)
const newNotification = ref({
  title: '',
  message: '',
  recipients: 'all'
})

const templates = {
  system_maintenance: {
    title: 'System Maintenance Scheduled',
    message: 'We will be performing system maintenance on [date]. The system may be unavailable during this time.'
  },
  new_feature: {
    title: 'New Feature Available',
    message: 'We have added a new feature to improve your experience. Check it out!'
  },
  general_announcement: {
    title: 'Important Announcement',
    message: 'Please read this important announcement regarding our services.'
  }
}

const fetchNotifications = async () => {
  try {
    const token = localStorage.getItem('auth_token')
    const response = await fetch('http://localhost:8000/admin/notifications/history', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      notifications.value = result.data.notifications || []
    }
  } catch (error) {
    console.error('Error fetching notifications:', error)
  }
}

const selectTemplate = (templateKey) => {
  const template = templates[templateKey]
  newNotification.value.title = template.title
  newNotification.value.message = template.message
  showSendModal.value = true
}

const sendNotification = async () => {
  try {
    const token = localStorage.getItem('auth_token')

    // Map recipient types to backend format
    let recipientType = 'all_clients'
    if (newNotification.value.recipients === 'experts') recipientType = 'all_experts'
    else if (newNotification.value.recipients === 'admins') recipientType = 'specific'
    else if (newNotification.value.recipients === 'all') recipientType = 'all_clients' // Default to clients

    const response = await fetch('http://localhost:8000/admin/notifications/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        recipient_type: recipientType,
        subject: newNotification.value.title,
        message: newNotification.value.message
      })
    })

    if (response.ok) {
      showSendModal.value = false
      newNotification.value = { title: '', message: '', recipients: 'all' }
      fetchNotifications()
    }
  } catch (error) {
    console.error('Error sending notification:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchNotifications()
})
</script>
