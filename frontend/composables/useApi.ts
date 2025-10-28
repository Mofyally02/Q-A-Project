import { useRuntimeConfig } from '#app'
import { useAuthStore } from '~/stores/auth'

export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase || 'http://localhost:8000'

  const api = $fetch.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Authentication
  const login = async (email: string, password: string) => {
    return await api('/auth/login', {
      method: 'POST',
      body: { email, password }
    })
  }

  const register = async (userData: any) => {
    return await api('/auth/register', {
      method: 'POST',
      body: userData
    })
  }

  const registerClient = async (userData: any) => {
    return await api('/auth/register/client', {
      method: 'POST',
      body: { ...userData, role: 'client' }
    })
  }

  const registerExpert = async (userData: any) => {
    return await api('/auth/register/expert', {
      method: 'POST',
      body: { ...userData, role: 'expert' }
    })
  }

  // Role-specific login endpoints
  const loginClient = async (email: string, password: string) => {
    return await api('/auth/login/client', {
      method: 'POST',
      body: { email, password }
    })
  }

  const loginExpert = async (email: string, password: string) => {
    return await api('/auth/login/expert', {
      method: 'POST',
      body: { email, password }
    })
  }

  const loginAdmin = async (email: string, password: string) => {
    return await api('/auth/login/admin', {
      method: 'POST',
      body: { email, password }
    })
  }

  // Questions
  const submitQuestion = async (questionData: {
    content: string
    subject: string
    userId: string
    type?: 'text' | 'image'
    imageUrl?: string
  }) => {
    return await api('/questions/submit', {
      method: 'POST',
      body: questionData
    })
  }

  const getQuestions = async (userId?: string, status?: string) => {
    const params = new URLSearchParams()
    if (userId) params.append('user_id', userId)
    if (status) params.append('status', status)
    
    return await api(`/questions?${params.toString()}`)
  }

  const getQuestionById = async (questionId: string) => {
    return await api(`/questions/${questionId}`)
  }

  // AI Service
  const processWithAI = async (questionId: string) => {
    return await api(`/ai/process/${questionId}`, {
      method: 'POST'
    })
  }

  const getAIResponse = async (questionId: string) => {
    return await api(`/ai/response/${questionId}`)
  }

  // Expert Reviews
  const getPendingReviews = async (expertId: string, subjects: string[]) => {
    return await api('/expert/reviews/pending', {
      method: 'POST',
      body: { expertId, subjects }
    })
  }

  const submitExpertReview = async (reviewData: {
    questionId: string
    expertId: string
    decision: 'approved' | 'rejected'
    notes?: string
  }) => {
    return await api('/expert/reviews/submit', {
      method: 'POST',
      body: reviewData
    })
  }

  // Poe API Integration
  const queryPoeModels = async (models: string[], question: string, subject: string) => {
    return await api('/poe/query-multiple', {
      method: 'POST',
      body: { models, question, subject }
    })
  }

  const getPoeModels = async () => {
    return await api('/poe/models')
  }

  // Humanization
  const humanizeResponse = async (responseId: string) => {
    return await api(`/humanization/process/${responseId}`, {
      method: 'POST'
    })
  }

  // Originality Check
  const checkOriginality = async (responseId: string) => {
    return await api(`/originality/check/${responseId}`, {
      method: 'POST'
    })
  }

  // Admin Functions
  const getUsers = async () => {
    return await api('/admin/users')
  }

  const updateUserSubjects = async (userId: string, subjects: string[]) => {
    return await api(`/admin/users/${userId}/subjects`, {
      method: 'PUT',
      body: { subjects }
    })
  }

  const getSystemStats = async () => {
    return await api('/admin/stats')
  }

  // WebSocket connection for real-time updates
  const connectWebSocket = (onMessage: (data: any) => void, onError?: (error: any) => void) => {
    // Get current user from auth store
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated || !authStore.user) {
      console.error('Cannot connect WebSocket: User not authenticated')
      return null
    }

    const userId = authStore.user.id
    const wsUrl = config.public.wsUrl || `ws://localhost:8000/ws/${userId}`
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('WebSocket message parse error:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (ws.readyState === WebSocket.CLOSED) {
          connectWebSocket(onMessage, onError)
        }
      }, 5000)
    }
    
    return ws
  }

  return {
    // Authentication
    login,
    register,
    registerClient,
    registerExpert,
    loginClient,
    loginExpert,
    loginAdmin,
    
    // Questions
    submitQuestion,
    getQuestions,
    getQuestionById,
    
    // AI Service
    processWithAI,
    getAIResponse,
    
    // Expert Reviews
    getPendingReviews,
    submitExpertReview,
    
    // Poe API
    queryPoeModels,
    getPoeModels,
    
    // Humanization & Originality
    humanizeResponse,
    checkOriginality,
    
    // Admin
    getUsers,
    updateUserSubjects,
    getSystemStats,
    
    // WebSocket
    connectWebSocket
  }
}
