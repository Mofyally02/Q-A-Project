<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Chat Interface Container -->
    <div class="h-screen flex">
      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col" :class="{ 'mr-96': showSidePanel }">
        <!-- Header -->
        <div class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                <Icon name="heroicons:chat-bubble-left-right" class="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 class="text-xl font-bold text-gray-900">AL-Tech Academy Q&A</h1>
                <p class="text-sm text-gray-500">
                  {{ getWelcomeMessage() }}
                </p>
              </div>
            </div>
            
            <!-- User Info & Actions -->
            <div class="flex items-center space-x-4">
              <!-- Toggle Panel Button -->
              <button 
                v-if="authStore.isAuthenticated && (authStore.hasRole('expert') || authStore.hasRole('admin'))"
                @click="toggleSidePanel"
                class="btn-secondary"
              >
                <Icon name="heroicons:bars-3" class="h-5 w-5" />
              </button>
              
              <div v-if="authStore.isAuthenticated" class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-white">{{ authStore.userInitials }}</span>
                </div>
                <span class="text-sm font-medium text-gray-700">{{ authStore.userName }}</span>
                <span class="badge-primary text-xs">{{ getRoleDisplayName(authStore.userRole) }}</span>
              </div>
              
              <button 
                v-if="authStore.isAuthenticated"
                @click="handleLogout"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5" />
              </button>
              
              <button 
                v-else
                @click="showLoginModal = true"
                class="btn-primary"
              >
                Sign In
              </button>
            </div>
          </div>
        </div>

        <!-- Chat Messages Area -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="chatContainer">
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Icon name="heroicons:academic-cap" class="h-8 w-8 text-primary-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ getWelcomeTitle() }}</h3>
            <p class="text-gray-600 max-w-md mx-auto">{{ getWelcomeDescription() }}</p>
          </div>

          <!-- Messages -->
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="flex"
            :class="message.sender === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div 
              class="max-w-3xl px-4 py-3 rounded-lg"
              :class="getMessageClasses(message)"
            >
              <!-- Message Header -->
              <div class="flex items-center space-x-2 mb-2">
                <Icon :name="getMessageIcon(message)" class="h-4 w-4" />
                <span class="text-xs font-medium">{{ getMessageSender(message) }}</span>
                <span class="text-xs text-gray-500">{{ formatTime(message.timestamp) }}</span>
              </div>
              
              <!-- Message Content -->
              <div class="prose prose-sm max-w-none">
                <div v-if="message.type === 'text'">
                  {{ message.content }}
                </div>
                
                <!-- Image Message -->
                <div v-else-if="message.type === 'image'" class="space-y-2">
                  <img 
                    :src="message.imageUrl" 
                    :alt="message.content"
                    class="max-w-sm rounded-lg shadow-sm"
                  >
                  <p class="text-sm text-gray-600">{{ message.content }}</p>
                </div>
                
                <!-- Question Status -->
                <div v-if="message.questionId" class="mt-3 flex items-center space-x-2">
                  <span class="badge" :class="getStatusBadgeClass(message.status)">
                    {{ message.status }}
                  </span>
                  <span class="text-xs text-gray-500">Question #{{ message.questionId }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex justify-start">
            <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
              <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
                <span class="text-sm text-gray-500">AI is thinking...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="bg-white border-t border-gray-200 p-6 flex-shrink-0">
          <form @submit.prevent="sendMessage" class="flex space-x-4">
            <!-- Subject Selection (for clients) -->
            <select 
              v-if="authStore.hasRole('client') && !currentMessage.type"
              v-model="selectedSubject"
              class="input-primary w-48"
            >
              <option value="">Select Subject</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Chemistry">Chemistry</option>
              <option value="Biology">Biology</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Engineering">Engineering</option>
              <option value="Business">Business</option>
              <option value="Other">Other</option>
            </select>

            <!-- Message Input -->
            <div class="flex-1 relative">
              <textarea
                v-model="currentMessage.content"
                @keydown.enter.prevent="handleEnterKey"
                placeholder="Type your message..."
                class="textarea-primary resize-none"
                rows="1"
                ref="messageInput"
              ></textarea>
            </div>

            <!-- Attachment Button -->
            <button
              type="button"
              @click="toggleAttachment"
              class="btn-secondary"
              :class="{ 'bg-primary-100 text-primary-600': showAttachmentOptions }"
            >
              <Icon name="heroicons:paper-clip" class="h-5 w-5" />
            </button>

            <!-- Send Button -->
            <button
              type="submit"
              :disabled="!canSendMessage"
              class="btn-primary"
            >
              <Icon name="heroicons:paper-airplane" class="h-5 w-5" />
            </button>
          </form>

          <!-- Attachment Options -->
          <div v-if="showAttachmentOptions" class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="grid grid-cols-2 gap-4">
              <button
                @click="selectImage"
                class="flex items-center space-x-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <Icon name="heroicons:photo" class="h-5 w-5 text-gray-600" />
                <span class="text-sm">Upload Image</span>
              </button>
              <button
                @click="selectFile"
                class="flex items-center space-x-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <Icon name="heroicons:document" class="h-5 w-5 text-gray-600" />
                <span class="text-sm">Upload File</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Side Panel (Expert/Admin) -->
      <div v-if="showSidePanel" class="fixed right-0 top-0 h-full w-96 z-40">
        <ExpertReviewPanel v-if="authStore.hasRole('expert')" />
        <AdminPanel v-else-if="authStore.hasRole('admin')" />
      </div>
    </div>

    <!-- Login Modal -->
    <div v-if="showLoginModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Sign In</h2>
        
        <div class="space-y-4">
          <button
            @click="loginWithDemo('client')"
            class="w-full btn-primary"
          >
            Client Demo
          </button>
          <button
            @click="loginWithDemo('expert')"
            class="w-full btn-secondary"
          >
            Expert Demo
          </button>
          <button
            @click="loginWithDemo('admin')"
            class="w-full btn-secondary"
          >
            Admin Demo
          </button>
        </div>
        
        <button
          @click="showLoginModal = false"
          class="mt-4 text-sm text-gray-500 hover:text-gray-700"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileUpload"
      class="hidden"
    >
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useQuestionsStore } from '~/stores/questions'
import { UserRole } from '~/types'
import ExpertReviewPanel from '~/components/ExpertReviewPanel.vue'
import AdminPanel from '~/components/AdminPanel.vue'

const authStore = useAuthStore()
const questionsStore = useQuestionsStore()
const toast = useToast()

// State
const messages = ref<any[]>([])
const currentMessage = ref({
  content: '',
  type: 'text' as 'text' | 'image',
  imageUrl: ''
})
const selectedSubject = ref('')
import { ref } from 'vue'

const showAttachmentOptions = ref(false)
const showLoginModal = ref(false)
const showSidePanel = ref(false)
const isTyping = ref(false)
const chatContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()
const fileInput = ref<HTMLInputElement>()

// Computed
const canSendMessage = computed(() => {
  if (!authStore.isAuthenticated) return false
  if (!currentMessage.value.content.trim()) return false
  if (authStore.hasRole('client') && !selectedSubject.value && !currentMessage.value.imageUrl) return false
  return true
})

// Methods
const getWelcomeMessage = () => {
  if (!authStore.isAuthenticated) return 'Sign in to start asking questions'
  
  switch (authStore.userRole) {
    case UserRole.CLIENT:
      return 'Ask me anything! I\'m here to help with your academic questions.'
    case UserRole.EXPERT:
      return 'Review and enhance AI responses for quality assurance.'
    case UserRole.ADMIN:
      return 'Monitor system performance and manage questions.'
    default:
      return 'Welcome to AL-Tech Academy Q&A System'
  }
}

const getRoleDisplayName = (role: string) => {
  switch (role) {
    case UserRole.CLIENT:
      return 'Student'
    case UserRole.EXPERT:
      return 'Expert'
    case UserRole.ADMIN:
      return 'Admin'
    default:
      return 'User'
  }
}

const getWelcomeTitle = () => {
  if (!authStore.isAuthenticated) return 'Welcome to AL-Tech Academy'
  
  switch (authStore.userRole) {
    case UserRole.CLIENT:
      return 'Ready to learn?'
    case UserRole.EXPERT:
      return 'Expert Review Dashboard'
    case UserRole.ADMIN:
      return 'Admin Control Panel'
    default:
      return 'Welcome'
  }
}

const getWelcomeDescription = () => {
  if (!authStore.isAuthenticated) return 'Sign in to start asking questions and get AI-powered answers'
  
  switch (authStore.userRole) {
    case UserRole.CLIENT:
      return 'Ask any academic question and get detailed, accurate answers powered by advanced AI models.'
    case UserRole.EXPERT:
      return 'Review AI-generated responses, make improvements, and ensure academic quality.'
    case UserRole.ADMIN:
      return 'Monitor question submissions, review system performance, and manage user activities.'
    default:
      return 'Get started by asking a question'
  }
}

const getMessageClasses = (message: any) => {
  const baseClasses = 'shadow-sm'
  
  if (message.sender === 'user') {
    return `${baseClasses} bg-primary-600 text-white`
  } else if (message.sender === 'ai') {
    return `${baseClasses} bg-white border border-gray-200 text-gray-900`
  } else if (message.sender === 'expert') {
    return `${baseClasses} bg-blue-50 border border-blue-200 text-blue-900`
  } else {
    return `${baseClasses} bg-gray-100 border border-gray-200 text-gray-700`
  }
}

const getMessageIcon = (message: any) => {
  switch (message.sender) {
    case 'user':
      return 'heroicons:user'
    case 'ai':
      return 'heroicons:cpu-chip'
    case 'expert':
      return 'heroicons:academic-cap'
    case 'system':
      return 'heroicons:information-circle'
    default:
      return 'heroicons:chat-bubble-left-right'
  }
}

const getMessageSender = (message: any) => {
  switch (message.sender) {
    case 'user':
      return 'You'
    case 'ai':
      return 'AI Assistant'
    case 'expert':
      return 'Expert Review'
    case 'system':
      return 'System'
    default:
      return 'Unknown'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'badge-warning'
    case 'processing':
      return 'badge-info'
    case 'completed':
      return 'badge-success'
    case 'failed':
      return 'badge-error'
    default:
      return 'badge-secondary'
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (event.shiftKey) {
    // Allow new line with Shift+Enter
    return
  }
  // Send message with Enter
  sendMessage()
}

const sendMessage = async () => {
  if (!canSendMessage.value) return
  
  try {
    const messageContent = currentMessage.value.content.trim()
    const messageType = currentMessage.value.type
    const imageUrl = currentMessage.value.imageUrl
    
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      content: messageContent,
      type: messageType,
      imageUrl: imageUrl,
      sender: 'user',
      timestamp: new Date().toISOString()
    }
    
    messages.value.push(userMessage)
    
    // Clear input
    currentMessage.value = {
      content: '',
      type: 'text',
      imageUrl: ''
    }
    selectedSubject.value = ''
    showAttachmentOptions.value = false
    
    // Show typing indicator
    isTyping.value = true
    
    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        content: `This is a sample AI response to: "${messageContent}". In a real implementation, this would be processed by the backend AI service.`,
        type: 'text',
        sender: 'ai',
        timestamp: new Date().toISOString(),
        questionId: Math.floor(Math.random() * 1000),
        status: 'completed'
      }
      
      messages.value.push(aiResponse)
      isTyping.value = false
      scrollToBottom()
    }, 2000)
    
    scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    toast.error('Failed to send message')
    isTyping.value = false
  }
}

const handleLogin = async (email: string, password: string) => {
  try {
    await authStore.login(email, password)
    showLoginModal.value = false
    toast.success('Login successful!')
  } catch (error) {
    toast.error('Login failed. Please check your credentials.')
  }
}

const toggleAttachment = () => {
  showAttachmentOptions.value = !showAttachmentOptions.value
}

const selectImage = () => {
  fileInput.value?.click()
}

const selectFile = () => {
  // Implement file selection
  toast.info('File upload coming soon')
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      currentMessage.value.imageUrl = e.target?.result as string
      currentMessage.value.type = 'image'
      showAttachmentOptions.value = false
    }
    reader.readAsDataURL(file)
  }
}

const handleLogout = async () => {
  await authStore.logout()
  messages.value = []
}

const loginWithDemo = async (role: string) => {
  try {
    const credentials = {
      client: { email: 'client@demo.com', password: 'demo123' },
      expert: { email: 'expert@demo.com', password: 'demo123' },
      admin: { email: 'admin@demo.com', password: 'demo123' }
    }
    
    const creds = credentials[role as keyof typeof credentials]
    await authStore.login(creds.email, creds.password)
    
    showLoginModal.value = false
    toast.success(`Welcome! Logged in as ${role}`)
  } catch (error) {
    toast.error('Demo login failed')
  }
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const toggleSidePanel = () => {
  showSidePanel.value = !showSidePanel.value
}

// Initialize auth on mount
onMounted(async () => {
  await authStore.initializeAuth()
})
</script>