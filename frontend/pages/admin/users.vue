<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
            <p class="mt-1 text-sm text-gray-500">Manage users, add experts, and assign roles</p>
          </div>
          <button
            @click="showAddExpertModal = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Add Expert
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by email or name..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
            <select
              v-model="filterRole"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Roles</option>
              <option value="client">Client</option>
              <option value="expert">Expert</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="fetchUsers"
              class="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in filteredUsers" :key="user.user_id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ user.first_name?.[0] }}{{ user.last_name?.[0] }}
                      </span>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ user.first_name }} {{ user.last_name }}
                      </div>
                      <div class="text-sm text-gray-500">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="{
                      'bg-blue-100 text-blue-800': user.role === 'client',
                      'bg-green-100 text-green-800': user.role === 'expert',
                      'bg-red-100 text-red-800': user.role === 'admin'
                    }"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                  >
                    {{ user.role }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(user.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click="viewUserDetails(user)"
                    class="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    View
                  </button>
                  <button
                    @click="editUserRole(user)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Edit Role
                  </button>
                </td>
              </tr>
              <tr v-if="!users.length">
                <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                  No users found
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6" v-if="users.length">
          <div class="flex-1 flex justify-between sm:hidden">
            <button class="btn-pagination">Previous</button>
            <button class="btn-pagination">Next</button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
                to <span class="font-medium">{{ Math.min(currentPage * pageSize, users.length) }}</span>
                of <span class="font-medium">{{ users.length }}</span> results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  @click="currentPage--"
                  :disabled="currentPage === 1"
                  class="px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium"
                  :class="currentPage === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'"
                >
                  Previous
                </button>
                <button
                  @click="currentPage++"
                  :disabled="currentPage * pageSize >= users.length"
                  class="px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium"
                  :class="currentPage * pageSize >= users.length ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Expert Modal -->
    <div
      v-if="showAddExpertModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="showAddExpertModal = false"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add Expert</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                v-model="newExpert.email"
                type="email"
                placeholder="expert@example.com"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Specialization</label>
              <input
                v-model="newExpert.specialization"
                type="text"
                placeholder="e.g., Mathematics, Physics"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="flex justify-end gap-3 pt-4">
              <button
                @click="showAddExpertModal = false"
                class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                @click="addExpert"
                class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                Add Expert
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Page meta
definePageMeta({
  middleware: 'admin',
  layout: 'dashboard'
})

const users = ref([])
const searchQuery = ref('')
const filterRole = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const showAddExpertModal = ref(false)
const newExpert = ref({
  email: '',
  specialization: ''
})

const filteredUsers = computed(() => {
  let filtered = users.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(u => 
      u.email.toLowerCase().includes(query) ||
      u.first_name?.toLowerCase().includes(query) ||
      u.last_name?.toLowerCase().includes(query)
    )
  }
  
  if (filterRole.value) {
    filtered = filtered.filter(u => u.role === filterRole.value)
  }
  
  return filtered
})

const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('auth_token')
    const roleParam = filterRole.value ? `&role=${filterRole.value}` : ''
    const response = await fetch(`http://localhost:8000/admin/users?skip=${(currentPage.value - 1) * pageSize.value}&limit=${pageSize.value}${roleParam}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      users.value = result.data.users || []
    }
  } catch (error) {
    console.error('Error fetching users:', error)
  }
}

const addExpert = async () => {
  // Implementation for adding expert
  console.log('Adding expert:', newExpert.value)
  showAddExpertModal.value = false
  fetchUsers()
}

const viewUserDetails = (user) => {
  // Navigate to user details or open modal
  console.log('Viewing user:', user)
}

const editUserRole = (user) => {
  // Open role edit modal
  console.log('Editing user role:', user)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.btn-pagination {
  @apply relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50;
}
</style>
