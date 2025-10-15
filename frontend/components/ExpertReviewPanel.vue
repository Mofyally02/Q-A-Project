<template>
  <div class="h-full bg-white flex flex-col">
    <!-- Expert Panel Header -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Expert Review Panel</h2>
          <p class="text-sm text-gray-500">Review and approve AI responses</p>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <span class="text-xs text-gray-500">Online</span>
        </div>
      </div>
      
      <!-- Expert Subject Filter -->
      <div class="flex items-center space-x-2">
        <span class="text-sm font-medium text-gray-700">Your Subjects:</span>
        <div class="flex flex-wrap gap-1">
          <span 
            v-for="subject in expertSubjects" 
            :key="subject"
            class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
          >
            {{ subject }}
          </span>
        </div>
      </div>
    </div>

    <!-- Review Queue Stats -->
    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-3 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-yellow-600">{{ pendingReviews.length }}</div>
          <div class="text-xs text-gray-500">Pending</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">{{ reviewedToday }}</div>
          <div class="text-xs text-gray-500">Reviewed Today</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-600">{{ approvalRate }}%</div>
          <div class="text-xs text-gray-500">Approval Rate</div>
        </div>
      </div>
    </div>

    <!-- Review Queue -->
    <div class="flex-1 overflow-y-auto">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Review Queue</h3>
          <button 
            @click="refreshQueue"
            class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            :disabled="isRefreshing"
          >
            <Icon name="heroicons:arrow-path" class="h-4 w-4" :class="{ 'animate-spin': isRefreshing }" />
          </button>
        </div>
        
        <!-- Empty State -->
        <div v-if="pendingReviews.length === 0" class="text-center py-12">
          <Icon name="heroicons:check-circle" class="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h4 class="text-lg font-medium text-gray-900 mb-2">All caught up!</h4>
          <p class="text-gray-500">No pending reviews for your subjects.</p>
        </div>
        
        <!-- Review List -->
        <div v-else class="space-y-4">
          <div 
            v-for="review in pendingReviews" 
            :key="review.id"
            @click="selectReview(review)"
            class="p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 hover:shadow-sm transition-all"
            :class="{ 'border-blue-300 bg-blue-50': selectedReview?.id === review.id }"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                    {{ review.subject }}
                  </span>
                  <span class="text-xs text-gray-500">{{ formatTime(review.submittedAt) }}</span>
                </div>
                <h4 class="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
                  {{ review.question }}
                </h4>
                <p class="text-xs text-gray-500">
                  Asked by: {{ review.userName }}
                </p>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <Icon name="heroicons:chevron-right" class="h-4 w-4 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Review Details -->
    <div v-if="selectedReview" class="border-t border-gray-200 bg-gray-50">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Review Details</h3>
          <button 
            @click="selectedReview = null"
            class="p-1 rounded hover:bg-gray-200"
          >
            <Icon name="heroicons:x-mark" class="h-4 w-4" />
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- Question -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Original Question</label>
            <div class="p-3 bg-white border border-gray-200 rounded-lg">
              <p class="text-sm text-gray-900">{{ selectedReview.question }}</p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-gray-500">Subject: {{ selectedReview.subject }}</span>
                <span class="text-xs text-gray-500">{{ formatTime(selectedReview.submittedAt) }}</span>
              </div>
            </div>
          </div>
          
          <!-- AI Response -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">AI Response</label>
            <div class="p-3 bg-white border border-gray-200 rounded-lg">
              <p class="text-sm text-gray-900 whitespace-pre-wrap">{{ selectedReview.aiResponse }}</p>
            </div>
          </div>
          
          <!-- Expert Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Expert Notes (Optional)</label>
            <textarea 
              v-model="expertNotes"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows="3"
              placeholder="Add any notes about your review decision..."
            ></textarea>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex space-x-3 pt-4">
            <button 
              @click="approveReview"
              :disabled="isProcessing"
              class="flex-1 flex items-center justify-center space-x-2 bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Icon name="heroicons:check" class="h-4 w-4" />
              <span>Approve</span>
            </button>
            <button 
              @click="rejectReview"
              :disabled="isProcessing"
              class="flex-1 flex items-center justify-center space-x-2 bg-red-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Icon name="heroicons:x-mark" class="h-4 w-4" />
              <span>Reject</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { type PendingReview, type ExpertReview } from '~/types'

const authStore = useAuthStore()
const toast = useToast()

// State
const pendingReviews = ref<PendingReview[]>([])
const selectedReview = ref<PendingReview | null>(null)
const expertNotes = ref('')
const isProcessing = ref(false)
const isRefreshing = ref(false)
const reviewedToday = ref(0)
const approvalRate = ref(85)

// Computed
const expertSubjects = computed(() => {
  return authStore.user?.subjects || []
})

// Methods
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

const refreshQueue = async () => {
  isRefreshing.value = true
  try {
    await fetchPendingReviews()
  } finally {
    isRefreshing.value = false
  }
}

const fetchPendingReviews = async () => {
  try {
    const api = useApi()
    const response = await api.getPendingReviews(authStore.user!.id, expertSubjects.value)
    
    if (response.success) {
      pendingReviews.value = response.data
    } else {
      console.error('Failed to fetch pending reviews:', response.message)
      toast.error('Failed to load pending reviews')
    }
  } catch (error) {
    console.error('Error fetching pending reviews:', error)
    toast.error('Failed to load pending reviews')
  }
}

const selectReview = (review: PendingReview) => {
  selectedReview.value = review
  expertNotes.value = ''
}

const approveReview = async () => {
  if (!selectedReview.value) return
  
  isProcessing.value = true
  try {
    const api = useApi()
    const response = await api.submitExpertReview({
      questionId: selectedReview.value.questionId,
      expertId: authStore.user!.id,
      decision: 'approved',
      notes: expertNotes.value || undefined
    })
    
    if (response.success) {
      // Remove from pending queue
      pendingReviews.value = pendingReviews.value.filter(r => r.id !== selectedReview.value!.id)
      selectedReview.value = null
      expertNotes.value = ''
      
      // Update stats
      reviewedToday.value++
      
      toast.success('Response approved successfully!')
    } else {
      throw new Error(response.message || 'Failed to approve response')
    }
  } catch (error) {
    console.error('Error approving review:', error)
    toast.error('Failed to approve response')
  } finally {
    isProcessing.value = false
  }
}

const rejectReview = async () => {
  if (!selectedReview.value) return
  
  isProcessing.value = true
  try {
    const api = useApi()
    const response = await api.submitExpertReview({
      questionId: selectedReview.value.questionId,
      expertId: authStore.user!.id,
      decision: 'rejected',
      notes: expertNotes.value || undefined
    })
    
    if (response.success) {
      // Remove from pending queue
      pendingReviews.value = pendingReviews.value.filter(r => r.id !== selectedReview.value!.id)
      selectedReview.value = null
      expertNotes.value = ''
      
      // Update stats
      reviewedToday.value++
      
      toast.success('Response rejected and sent back for revision')
    } else {
      throw new Error(response.message || 'Failed to reject response')
    }
  } catch (error) {
    console.error('Error rejecting review:', error)
    toast.error('Failed to reject response')
  } finally {
    isProcessing.value = false
  }
}

// Initialize
onMounted(() => {
  fetchPendingReviews()
})

// Auto-refresh every 30 seconds
onMounted(() => {
  const interval = setInterval(fetchPendingReviews, 30000)
  onUnmounted(() => clearInterval(interval))
})
</script>