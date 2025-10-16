<template>
  <div id="app" class="h-screen bg-gray-100 flex">
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="flex flex-col items-center space-y-4">
        <div class="spinner w-8 h-8"></div>
        <p class="text-gray-600 font-medium">Loading AL-Tech Academy Q&A...</p>
      </div>
    </div>

    <!-- Main App Layout -->
    <div v-else class="flex w-full h-full">
      <!-- Sidebar -->
      <div class="w-80 bg-white border-r border-gray-200 flex flex-col" :class="{ 'hidden lg:flex': !showSidebar }">
        <!-- Sidebar Header -->
        <div class="p-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Icon name="heroicons:academic-cap" class="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 class="text-lg font-semibold text-gray-900">AL-Tech Academy</h1>
                <p class="text-xs text-gray-500">AI-Powered Q&A</p>
              </div>
            </div>
            <button 
              @click="toggleSidebar"
              class="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Icon name="heroicons:x-mark" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <!-- User Info -->
        <div v-if="authStore.isAuthenticated" class="p-4 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span class="text-sm font-bold text-white">{{ authStore.userInitials }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ authStore.userName }}</p>
              <p class="text-xs text-gray-500">{{ getRoleDisplayName(authStore.userRole) }}</p>
            </div>
            <button 
              @click="handleLogout"
              class="p-1 rounded hover:bg-gray-100"
            >
              <Icon name="heroicons:arrow-right-on-rectangle" class="h-4 w-4 text-gray-400" />
            </button>
          </div>
        </div>

        <!-- Login Section -->
        <div v-else class="p-4 border-b border-gray-200">
          <button 
            @click="showLoginModal = true"
            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
          >
            Sign In to Start
          </button>
        </div>

        <!-- Chat History -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Recent Conversations</h3>
            
            <!-- Chat List -->
            <div class="space-y-2">
              <div 
                v-for="chat in chatHistory" 
                :key="chat.id"
                @click="selectChat(chat)"
                class="p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
                :class="{ 'bg-blue-50 border border-blue-200': selectedChat?.id === chat.id }"
              >
                <div class="flex items-start space-x-3">
                  <div class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Icon :name="getChatIcon(chat)" class="h-4 w-4 text-gray-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ chat.title }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ chat.lastMessage }}</p>
                    <p class="text-xs text-gray-400">{{ formatChatTime(chat.updatedAt) }}</p>
                  </div>
                  <div v-if="chat.status === 'pending'" class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <div v-else-if="chat.status === 'processing'" class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  <div v-else-if="chat.status === 'completed'" class="w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-if="chatHistory.length === 0" class="text-center py-8">
                <Icon name="heroicons:chat-bubble-left-ellipsis" class="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">No conversations yet</p>
                <p class="text-xs text-gray-400">Start asking questions!</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Footer -->
        <div class="p-4 border-t border-gray-200">
          <button 
            @click="startNewChat"
            class="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            <Icon name="heroicons:plus" class="h-4 w-4" />
            <span>New Question</span>
          </button>
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col">
        <!-- Chat Header -->
        <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button 
              @click="toggleSidebar"
              class="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Icon name="heroicons:bars-3" class="h-5 w-5" />
            </button>
            
            <div v-if="selectedChat">
              <h2 class="text-lg font-semibold text-gray-900">{{ selectedChat.title }}</h2>
              <p class="text-sm text-gray-500">{{ selectedChat.subject }}</p>
            </div>
            <div v-else>
              <h2 class="text-lg font-semibold text-gray-900">AL-Tech Academy Q&A</h2>
              <p class="text-sm text-gray-500">Ask me anything!</p>
            </div>
          </div>

          <!-- Chat Actions -->
          <div class="flex items-center space-x-2">
            <div v-if="selectedChat?.status" class="flex items-center space-x-2">
              <span class="text-xs px-2 py-1 rounded-full" :class="getStatusBadgeClass(selectedChat.status)">
                {{ selectedChat.status }}
              </span>
            </div>
            
            <!-- Expert Panel Toggle -->
            <button 
              v-if="authStore.hasRole('expert') || authStore.hasRole('admin')"
              @click="toggleExpertPanel"
              class="p-2 rounded-lg hover:bg-gray-100"
            >
              <Icon name="heroicons:cog-6-tooth" class="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </div>

        <!-- Messages Area -->
        <div class="flex-1 overflow-y-auto bg-gray-50" ref="messagesContainer">
          <div class="max-w-4xl mx-auto p-6 space-y-6">
            <!-- Welcome Message -->
            <div v-if="!selectedChat || !selectedChat.messages || selectedChat.messages.length === 0" class="text-center py-12">
              <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Icon name="heroicons:academic-cap" class="h-10 w-10 text-white" />
              </div>
              <h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to AL-Tech Academy</h3>
              <p class="text-gray-600 max-w-md mx-auto mb-8">
                Get instant, accurate answers to your academic questions powered by advanced AI technology.
              </p>
              <button 
                @click="startNewChat"
                class="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
              >
                Start Your First Question
              </button>
            </div>

            <!-- Messages -->
            <div v-if="selectedChat" class="space-y-4">
              <div 
                v-for="message in selectedChat.messages" 
                :key="message.id"
                class="flex"
                :class="message.sender === 'user' ? 'justify-end' : 'justify-start'"
              >
                <div 
                  class="max-w-2xl px-4 py-3 rounded-2xl"
                  :class="getMessageClasses(message)"
                >
                  <div v-if="message.sender !== 'user'" class="flex items-center space-x-2 mb-2">
                    <Icon :name="getMessageIcon(message)" class="h-4 w-4" />
                    <span class="text-xs font-medium text-gray-600">{{ getMessageSender(message) }}</span>
                  </div>
                  
                  <div class="prose prose-sm max-w-none">
                    <div v-if="message.type === 'text'" v-html="message.content"></div>
                    
                    <!-- Image Message -->
                    <div v-else-if="message.type === 'image'" class="space-y-2">
                      <img 
                        :src="message.imageUrl" 
                        :alt="message.content"
                        class="max-w-sm rounded-lg shadow-sm"
                      >
                      <p class="text-sm text-gray-600">{{ message.content }}</p>
                    </div>
                  </div>
                  
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
                    <div v-if="message.status" class="flex items-center space-x-2">
                      <span class="text-xs px-2 py-1 rounded-full" :class="getStatusBadgeClass(message.status)">
                        {{ message.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Typing Indicator -->
              <div v-if="isTyping" class="flex justify-start">
                <div class="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
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
          </div>
        </div>

        <!-- Input Area -->
        <div class="bg-white border-t border-gray-200 p-4">
          <div class="max-w-4xl mx-auto">
            <form @submit.prevent="sendMessage" class="flex items-end space-x-3">
              <!-- Subject Selection -->
              <div v-if="!selectedChat && authStore.hasRole('client')" class="w-48">
                <select 
                  v-model="newChatSubject"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
              </div>

              <!-- Message Input -->
              <div class="flex-1 relative">
                <textarea
                  v-model="currentMessage"
                  @keydown.enter.prevent="handleEnterKey"
                  placeholder="Type your question..."
                  class="w-full px-4 py-3 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="1"
                  ref="messageInput"
                ></textarea>
                
                <!-- Attachment Button -->
                <button
                  type="button"
                  @click="toggleAttachment"
                  class="absolute right-3 bottom-3 p-1 rounded-full hover:bg-gray-100"
                >
                  <Icon name="heroicons:paper-clip" class="h-5 w-5 text-gray-500" />
                </button>
              </div>

              <!-- Send Button -->
              <button
                type="submit"
                :disabled="!canSendMessage"
                class="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                <Icon name="heroicons:paper-airplane" class="h-5 w-5" />
              </button>
            </form>

            <!-- Attachment Options -->
            <div v-if="showAttachmentOptions" class="mt-3 p-3 bg-gray-50 rounded-lg">
              <div class="flex space-x-3">
                <button
                  @click="selectImage"
                  class="flex items-center space-x-2 px-3 py-2 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
                >
                  <Icon name="heroicons:photo" class="h-4 w-4 text-gray-600" />
                  <span class="text-sm">Upload Image</span>
                </button>
                <button
                  @click="selectFile"
                  class="flex items-center space-x-2 px-3 py-2 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
                >
                  <Icon name="heroicons:document" class="h-4 w-4 text-gray-600" />
                  <span class="text-sm">Upload File</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Expert Panel -->
      <div v-if="showExpertPanel && (authStore.hasRole('expert') || authStore.hasRole('admin'))" class="w-96 bg-white border-l border-gray-200">
        <ExpertReviewPanel v-if="authStore.hasRole('expert')" />
        <AdminPanel v-else-if="authStore.hasRole('admin')" />
      </div>
    </div>

    <!-- Login/Signup Modal -->
    <div v-if="showLoginModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="bg-white rounded-2xl p-8 w-full max-w-md mx-4">
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Icon name="heroicons:academic-cap" class="h-8 w-8 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            {{ isSignupMode ? 'Create Account' : 'Welcome Back' }}
          </h2>
          <p class="text-gray-600">
            {{ isSignupMode ? 'Join AL-Tech Academy today' : 'Sign in to your account' }}
          </p>
        </div>

        <!-- Toggle between Login and Signup -->
        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            @click="isSignupMode = false"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              !isSignupMode 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            Sign In
          </button>
          <button
            @click="isSignupMode = true"
            :class="[
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              isSignupMode 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            Sign Up
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="!isSignupMode" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="login-email" class="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              id="login-email"
              v-model="loginForm.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your email"
            >
          </div>
          
          <div>
            <label for="login-password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            >
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <span v-if="authStore.isLoading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Signing In...
            </span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <!-- Signup Form -->
        <form v-else @submit.prevent="handleSignup" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="signup-firstname" class="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                id="signup-firstname"
                v-model="signupForm.firstName"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="First name"
              >
            </div>
            
            <div>
              <label for="signup-lastname" class="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                id="signup-lastname"
                v-model="signupForm.lastName"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Last name"
              >
            </div>
          </div>

          <div>
            <label for="signup-email" class="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              id="signup-email"
              v-model="signupForm.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your email"
            >
          </div>
          
          <div>
            <label for="signup-password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="signup-password"
              v-model="signupForm.password"
              type="password"
              required
              minlength="8"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Create a password (min 8 characters)"
            >
          </div>

          <div>
            <label for="signup-role" class="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <select
              id="signup-role"
              v-model="signupForm.role"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select your role</option>
              <option value="client">Student - Ask Questions</option>
              <option value="expert">Expert - Review Answers</option>
              <option value="admin">Admin - System Management</option>
            </select>
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <span v-if="authStore.isLoading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating Account...
            </span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <!-- Demo Login Section -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-center text-sm text-gray-500 mb-3">Or try with demo accounts</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              @click="loginWithDemo('client')"
              class="px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Student
            </button>
            <button
              @click="loginWithDemo('expert')"
              class="px-3 py-2 text-xs bg-orange-50 text-orange-700 rounded-lg hover:bg-orange-100 transition-colors"
            >
              Expert
            </button>
            <button
              @click="loginWithDemo('admin')"
              class="px-3 py-2 text-xs bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
            >
              Admin
            </button>
          </div>
        </div>
        
        <button
          @click="showLoginModal = false"
          class="mt-6 w-full text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          Maybe Later
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
import { UserRole, type User } from '~/types'
import ExpertReviewPanel from '~/components/ExpertReviewPanel.vue'
import AdminPanel from '~/components/AdminPanel.vue'

const authStore = useAuthStore()
const questionsStore = useQuestionsStore()
const toast = useToast()

// Global loading state
const isLoading = ref(true)

// UI State
const showSidebar = ref(true)
const showExpertPanel = ref(false)
const showLoginModal = ref(false)
const showAttachmentOptions = ref(false)
const isSignupMode = ref(false)

// Form data
const loginForm = ref({
  email: '',
  password: ''
})

const signupForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  role: ''
})

// Chat State
const chatHistory = ref<any[]>([])
const selectedChat = ref<any>(null)
const currentMessage = ref('')
const newChatSubject = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()
const fileInput = ref<HTMLInputElement>()

// Computed
const canSendMessage = computed(() => {
  if (!authStore.isAuthenticated) return false
  if (!currentMessage.value.trim()) return false
  if (!selectedChat.value && authStore.hasRole('client') && !newChatSubject.value) return false
  return true
})

// Methods
const getRoleDisplayName = (role: string) => {
  switch (role) {
    case UserRole.CLIENT:
      return 'Student'
    case UserRole.EXPERT:
      return 'Expert Editor'
    case UserRole.ADMIN:
      return 'System Admin'
    default:
      return 'User'
  }
}

const getChatIcon = (chat: any) => {
  switch (chat.subject) {
    case 'Mathematics':
      return 'heroicons:calculator'
    case 'Physics':
      return 'heroicons:bolt'
    case 'Chemistry':
      return 'heroicons:beaker'
    case 'Biology':
      return 'heroicons:heart'
    case 'Computer Science':
      return 'heroicons:computer-desktop'
    case 'Engineering':
      return 'heroicons:cog-6-tooth'
    case 'Business':
      return 'heroicons:briefcase'
    default:
      return 'heroicons:question-mark-circle'
  }
}

const getMessageClasses = (message: any) => {
  if (message.sender === 'user') {
    return 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
  } else if (message.sender === 'ai') {
    return 'bg-white border border-gray-200 text-gray-900 shadow-sm'
  } else if (message.sender === 'expert') {
    return 'bg-blue-50 border border-blue-200 text-blue-900'
  } else {
    return 'bg-gray-100 border border-gray-200 text-gray-700'
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
      return 'bg-yellow-100 text-yellow-800'
    case 'processing':
      return 'bg-blue-100 text-blue-800'
    case 'ai_responded':
      return 'bg-purple-100 text-purple-800'
    case 'expert_review':
      return 'bg-orange-100 text-orange-800'
    case 'approved':
      return 'bg-green-100 text-green-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatChatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

const toggleExpertPanel = () => {
  showExpertPanel.value = !showExpertPanel.value
}

const toggleAttachment = () => {
  showAttachmentOptions.value = !showAttachmentOptions.value
}

const startNewChat = () => {
  selectedChat.value = null
  currentMessage.value = ''
  newChatSubject.value = ''
  showSidebar.value = false
  messageInput.value?.focus()
}

const selectChat = (chat: any) => {
  selectedChat.value = chat
  showSidebar.value = false
  scrollToBottom()
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (event.shiftKey) return
  sendMessage()
}

const sendMessage = async () => {
  if (!canSendMessage.value) return
  
  try {
    const messageContent = currentMessage.value.trim()
    
    // Create new chat if none selected
    if (!selectedChat.value) {
      const newChat = {
        id: Date.now().toString(),
        title: messageContent.substring(0, 50) + (messageContent.length > 50 ? '...' : ''),
        subject: newChatSubject.value || 'General',
        status: 'processing',
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastMessage: messageContent
      }
      
      chatHistory.value.unshift(newChat)
      selectedChat.value = newChat
    }
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      content: messageContent,
      type: 'text',
      sender: 'user',
      timestamp: new Date().toISOString()
    }
    
    selectedChat.value.messages.push(userMessage)
    selectedChat.value.lastMessage = messageContent
    selectedChat.value.updatedAt = new Date().toISOString()
    
    // Clear input
    currentMessage.value = ''
    newChatSubject.value = ''
    showAttachmentOptions.value = false
    
    // Show typing indicator
    isTyping.value = true
    selectedChat.value.status = 'processing'
    
    // Submit question to backend
    const questionsStore = useQuestionsStore()
    const response = await questionsStore.submitQuestion(
      messageContent,
      selectedChat.value.subject,
      authStore.user!.id,
      'text'
    )
    
    if (response.success) {
      // Process with AI
      const api = useApi()
      let aiResponse
      try {
        aiResponse = await api.processWithAI(response.data.id)
      } catch (err) {
        console.error('Error processing with AI:', err)
        toast.error('AI processing failed. Please try again later.')
        isTyping.value = false
        selectedChat.value.status = 'failed'
        return
      }

      if (aiResponse && aiResponse.success && aiResponse.data && aiResponse.data.response) {
        // Add AI response to chat
        const aiMessage = {
          id: Date.now() + 1,
          content: aiResponse.data.response,
          type: 'text',
          sender: 'ai',
          timestamp: new Date().toISOString(),
          status: 'ai_responded'
        }
        
        selectedChat.value.messages.push(aiMessage)
        selectedChat.value.status = 'expert_review'
        isTyping.value = false
        
        // Add system message about expert review
        const systemMessage = {
          id: Date.now() + 1.5,
          content: `📋 Your question has been sent to our ${selectedChat.value.subject} expert for review. You'll receive the final answer once it's approved.`,
          type: 'text',
          sender: 'system',
          timestamp: new Date().toISOString(),
          status: 'processing'
        }
        
        selectedChat.value.messages.push(systemMessage)
        
        toast.success('Question submitted successfully!')
      } else {
        throw new Error(aiResponse.message || 'Failed to process with AI')
      }
    } else {
      throw new Error(response.message || 'Failed to submit question')
    }
    
    scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    toast.error('Failed to send message')
    isTyping.value = false
    selectedChat.value.status = 'failed'
  }
}

const selectImage = () => {
  fileInput.value?.click()
}

const selectFile = () => {
  toast.info('File upload coming soon')
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    toast.success(`File "${file.name}" uploaded successfully`)
  }
}

const handleLogout = async () => {
  await authStore.logout()
  chatHistory.value = []
  selectedChat.value = null
}

const handleLogin = async () => {
  try {
    await authStore.login(loginForm.value.email, loginForm.value.password)
    showLoginModal.value = false
    toast.success('Login successful!')
    
    // Reset form
    loginForm.value = { email: '', password: '' }
    
    // Load user's chat history
    await loadUserChatHistory()
  } catch (error) {
    console.error('Login error:', error)
    toast.error('Login failed. Please check your credentials.')
  }
}

const handleSignup = async () => {
  try {
    await authStore.register(
      signupForm.value.email,
      signupForm.value.password,
      `${signupForm.value.firstName} ${signupForm.value.lastName}`,
      signupForm.value.role as any
    )
    showLoginModal.value = false
    toast.success('Account created successfully!')
    
    // Reset form
    signupForm.value = {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      role: ''
    }
    
    // Load user's chat history
    await loadUserChatHistory()
  } catch (error) {
    console.error('Signup error:', error)
    toast.error('Signup failed. Please try again.')
  }
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
    
    // Load demo data based on role
    if (role === 'client') {
      chatHistory.value = [
        {
          id: '1',
          title: 'What is the derivative of x²?',
          subject: 'Mathematics',
          status: 'completed',
          messages: [
            {
              id: '1-1',
              content: 'What is the derivative of x²?',
              type: 'text',
              sender: 'user',
              timestamp: new Date(Date.now() - 3600000).toISOString()
            },
            {
              id: '1-2',
              content: 'The derivative of x² is 2x. This follows from the power rule of differentiation.',
              type: 'text',
              sender: 'expert',
              timestamp: new Date(Date.now() - 3500000).toISOString(),
              status: 'approved'
            }
          ],
          createdAt: new Date(Date.now() - 3600000).toISOString(),
          updatedAt: new Date(Date.now() - 3500000).toISOString(),
          lastMessage: 'The derivative of x² is 2x...'
        }
      ]
    } else if (role === 'expert') {
      // Expert sees pending reviews in their panel
      chatHistory.value = []
    }
  } catch (error) {
    toast.error('Demo login failed')
  }
}

const loadUserChatHistory = async () => {
  try {
    if (authStore.isAuthenticated && authStore.user) {
      const api = useApi()
      const response = await api.getQuestions(authStore.user.id)
      
      if (response.success && response.data) {
        chatHistory.value = response.data.map((question: any) => ({
          id: question.question_id,
          title: question.content.substring(0, 50) + (question.content.length > 50 ? '...' : ''),
          subject: question.subject,
          status: question.status,
          messages: question.messages || [],
          createdAt: question.created_at,
          updatedAt: question.updated_at || question.created_at,
          lastMessage: question.content.substring(0, 100) + (question.content.length > 100 ? '...' : '')
        }))
      }
    }
  } catch (error) {
    console.error('Error loading chat history:', error)
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// WebSocket connection for real-time updates
let wsConnection: WebSocket | null = null

const handleNewQuestion = (payload: any) => {
  // Add new question to chat history if it belongs to current user
  if (payload.userId === authStore.user?.id) {
    const newChat = {
      id: payload.id,
      title: payload.content.substring(0, 50) + (payload.content.length > 50 ? '...' : ''),
      subject: payload.subject,
      status: payload.status,
      messages: [{
        id: payload.id + '-msg',
        content: payload.content,
        type: 'text',
        sender: 'user',
        timestamp: payload.createdAt
      }],
      createdAt: payload.createdAt,
      updatedAt: payload.createdAt,
      lastMessage: payload.content
    }
    
    chatHistory.value.unshift(newChat)
  }
}

const initializeWebSocket = () => {
  if (!authStore.isAuthenticated) return
  
  const api = useApi()
  wsConnection = api.connectWebSocket(
    (data) => {
      // Handle real-time updates
      switch (data.type) {
        case 'question_status_update':
          handleQuestionStatusUpdate(data.payload)
          break
        case 'expert_review_update':
          handleExpertReviewUpdate(data.payload)
          break
        case 'new_question':
          handleNewQuestion(data.payload)
          break
      }
    },
    (error) => {
      console.error('WebSocket error:', error)
    }
  )
}

const handleQuestionStatusUpdate = (payload: any) => {
  // Update chat status in real-time
  if (selectedChat.value && selectedChat.value.id === payload.questionId) {
    selectedChat.value.status = payload.status
  }
  
  // Update chat history
  const chat = chatHistory.value.find(c => c.id === payload.questionId)
  if (chat) {
    chat.status = payload.status
    chat.updatedAt = new Date().toISOString()
  }
}

const handleExpertReviewUpdate = (payload: any) => {
  // Update expert panel in real-time
  if (authStore.hasRole('expert')) {
    // Refresh expert panel
    const expertPanel = document.querySelector('.expert-panel')
    if (expertPanel) {
      // Fallback: just fetch questions to refresh expert panel
      if (questionsStore && typeof questionsStore.fetchQuestions === "function") {
        questionsStore.fetchQuestions(authStore.user?.id)
      }
    }
  }
}

// Initialize app
onMounted(async () => {
  try {
    await authStore.initializeAuth()
    
    if (authStore.isAuthenticated) {
      await questionsStore.fetchQuestions(authStore.user?.id)
      initializeWebSocket()
    }
  } catch (error) {
    console.error('App initialization error:', error)
  } finally {
    isLoading.value = false
  }
})

// Cleanup WebSocket on unmount
onUnmounted(() => {
  if (wsConnection) {
    wsConnection.close()
  }
})

// Meta tags
useHead({
  title: 'AL-Tech Academy Q&A System',
  meta: [
    { name: 'description', content: 'AI-Powered Q&A System for AL-Tech Academy' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ]
})

// SEO
useSeoMeta({
  title: 'AL-Tech Academy Q&A System',
  ogTitle: 'AL-Tech Academy Q&A System',
  description: 'AI-Powered Q&A System for AL-Tech Academy',
  ogDescription: 'AI-Powered Q&A System for AL-Tech Academy',
  ogImage: '/og-image.jpg',
  twitterCard: 'summary_large_image'
})
</script>

<style>
@import '~/assets/css/main.css';
</style>