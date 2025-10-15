import { defineStore } from 'pinia'
import { type Question, QuestionStatus, type APIResponse } from '~/types'

interface QuestionsState {
  questions: Question[]
  isLoading: boolean
  error: string | null
}

export const useQuestionsStore = defineStore('questions', {
  state: (): QuestionsState => ({
    questions: [],
    isLoading: false,
    error: null
  }),

  getters: {
    getQuestionsByStatus: (state) => (status: QuestionStatus) => {
      return state.questions.filter(q => q.status === status)
    },
    getQuestionsByUser: (state) => (userId: string) => {
      return state.questions.filter(q => q.userId === userId)
    },
    pendingQuestions: (state) => state.questions.filter(q => q.status === QuestionStatus.PENDING),
    completedQuestions: (state) => state.questions.filter(q => q.status === QuestionStatus.COMPLETED)
  },

  actions: {
    async fetchQuestions(userId?: string, status?: string) {
      this.isLoading = true
      this.error = null
      
      try {
        const api = useApi()
        const response = await api.getQuestions(userId, status)
        
        if (response.success) {
          this.questions = response.data
        } else {
          throw new Error(response.message || 'Failed to fetch questions')
        }
      } catch (error) {
        console.error('Error fetching questions:', error)
        this.error = 'Failed to fetch questions'
      } finally {
        this.isLoading = false
      }
    },

    async submitQuestion(content: string, subject: string, userId: string, type: 'text' | 'image' = 'text', imageUrl?: string): Promise<APIResponse<Question>> {
      this.isLoading = true
      this.error = null
      
      try {
        const api = useApi()
        const response = await api.submitQuestion({
          content,
          subject,
          userId,
          type,
          imageUrl
        })
        
        if (response.success) {
          this.questions.unshift(response.data)
          return response
        } else {
          throw new Error(response.message || 'Failed to submit question')
        }
      } catch (error) {
        console.error('Submit question error:', error)
        this.error = 'Failed to submit question'
        return {
          success: false,
          message: 'Failed to submit question',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      } finally {
        this.isLoading = false
      }
    },

    async updateQuestionStatus(questionId: string, status: QuestionStatus): Promise<APIResponse> {
      this.isLoading = true
      this.error = null
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const question = this.questions.find(q => q.id === questionId)
        if (question) {
          question.status = status
          question.updatedAt = new Date().toISOString()
        }
        
        return {
          success: true,
          message: 'Question status updated successfully'
        }
      } catch (error) {
        this.error = 'Failed to update question status'
        return {
          success: false,
          message: 'Failed to update question status',
          error: 'Failed to update question status'
        }
      } finally {
        this.isLoading = false
      }
    },

    clearError() {
      this.error = null
    }
  }
})