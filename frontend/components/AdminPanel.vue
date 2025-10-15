<template>
  <div class="h-full bg-white border-l border-gray-200 shadow-lg">
    <div class="p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Admin Dashboard</h2>
      
      <!-- Stats Overview -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="flex items-center">
            <Icon name="heroicons:question-mark-circle" class="h-8 w-8 text-blue-600" />
            <div class="ml-3">
              <p class="text-sm font-medium text-blue-600">Total Questions</p>
              <p class="text-2xl font-bold text-blue-900">1,247</p>
            </div>
          </div>
        </div>
        
        <div class="bg-green-50 p-4 rounded-lg">
          <div class="flex items-center">
            <Icon name="heroicons:users" class="h-8 w-8 text-green-600" />
            <div class="ml-3">
              <p class="text-sm font-medium text-green-600">Active Users</p>
              <p class="text-2xl font-bold text-green-900">342</p>
            </div>
          </div>
        </div>
        
        <div class="bg-yellow-50 p-4 rounded-lg">
          <div class="flex items-center">
            <Icon name="heroicons:clock" class="h-8 w-8 text-yellow-600" />
            <div class="ml-3">
              <p class="text-sm font-medium text-yellow-600">Pending Reviews</p>
              <p class="text-2xl font-bold text-yellow-900">23</p>
            </div>
          </div>
        </div>
        
        <div class="bg-purple-50 p-4 rounded-lg">
          <div class="flex items-center">
            <Icon name="heroicons:chart-bar" class="h-8 w-8 text-purple-600" />
            <div class="ml-3">
              <p class="text-sm font-medium text-purple-600">Success Rate</p>
              <p class="text-2xl font-bold text-purple-900">94.2%</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="space-y-4">
        <h3 class="text-sm font-medium text-gray-700">Recent Activity</h3>
        
        <div class="space-y-3">
          <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Icon name="heroicons:plus-circle" class="h-5 w-5 text-green-600" />
            <div class="flex-1">
              <p class="text-sm text-gray-900">New question submitted</p>
              <p class="text-xs text-gray-500">Mathematics - 2 minutes ago</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Icon name="heroicons:check-circle" class="h-5 w-5 text-blue-600" />
            <div class="flex-1">
              <p class="text-sm text-gray-900">Question approved by expert</p>
              <p class="text-xs text-gray-500">Physics - 5 minutes ago</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Icon name="heroicons:user-plus" class="h-5 w-5 text-purple-600" />
            <div class="flex-1">
              <p class="text-sm text-gray-900">New user registered</p>
              <p class="text-xs text-gray-500">Student - 10 minutes ago</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Expert Management -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Expert Management</h3>
        
        <div class="space-y-3">
          <div 
            v-for="expert in expertUsers" 
            :key="expert.id"
            class="p-3 bg-white border border-gray-200 rounded-lg"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-xs font-medium text-blue-600">{{ expert.name.charAt(0) }}</span>
                </div>
                <span class="text-sm font-medium text-gray-900">{{ expert.name }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ expert.subjects?.length || 0 }} subjects</span>
            </div>
            
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="subject in expert.subjects || []" 
                :key="subject"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
              >
                {{ subject }}
              </span>
              <button 
                v-if="!expert.subjects || expert.subjects.length === 0"
                @click="assignSubjects(expert)"
                class="text-xs text-gray-500 hover:text-blue-600"
              >
                Assign subjects
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
        
        <div class="space-y-2">
          <button class="w-full btn-secondary text-sm">
            <Icon name="heroicons:cog-6-tooth" class="h-4 w-4" />
            System Settings
          </button>
          <button class="w-full btn-secondary text-sm">
            <Icon name="heroicons:users" class="h-4 w-4" />
            Manage Users
          </button>
          <button class="w-full btn-secondary text-sm">
            <Icon name="heroicons:chart-bar-square" class="h-4 w-4" />
            View Analytics
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type User } from '~/types'
import { UserRole } from '~/types'

const toast = useToast()

// State
const expertUsers = ref<User[]>([])
const isLoading = ref(false)

// Methods
const fetchUsers = async () => {
  isLoading.value = true
  try {
    const api = useApi()
    const response = await api.getUsers()
    
    if (response.success) {
      expertUsers.value = response.data.filter((user: User) => user.role === UserRole.EXPERT)
    } else {
      throw new Error(response.message || 'Failed to fetch users')
    }
  } catch (error) {
    console.error('Error fetching users:', error)
    toast.error('Failed to load expert users')
  } finally {
    isLoading.value = false
  }
}

const assignSubjects = (expert: User) => {
  // In a real app, this would open a modal or navigate to a subject assignment page
  toast.info(`Assign subjects for ${expert.name} - Feature coming soon`)
}

const updateExpertSubjects = async (expertId: string, subjects: string[]) => {
  try {
    const api = useApi()
    const response = await api.updateUserSubjects(expertId, subjects)
    
    if (response.success) {
      const expert = expertUsers.value.find(e => e.id === expertId)
      if (expert) {
        expert.subjects = subjects
        expert.updatedAt = new Date().toISOString()
      }
      toast.success('Expert subjects updated successfully')
    } else {
      throw new Error(response.message || 'Failed to update expert subjects')
    }
  } catch (error) {
    console.error('Error updating expert subjects:', error)
    toast.error('Failed to update expert subjects')
  }
}

// Initialize
onMounted(() => {
  fetchUsers()
})
</script>