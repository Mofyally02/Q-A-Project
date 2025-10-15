export enum UserRole {
  CLIENT = 'client',
  EXPERT = 'expert',
  ADMIN = 'admin'
}

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  avatar?: string
  subjects?: string[] // For experts - their assigned subjects
  createdAt: string
  updatedAt: string
}

export interface Question {
  id: string
  content: string
  subject: string
  status: QuestionStatus
  userId: string
  createdAt: string
  updatedAt: string
}

export enum QuestionStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  AI_RESPONDED = 'ai_responded',
  EXPERT_REVIEW = 'expert_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface Message {
  id: string
  content: string
  type: 'text' | 'image'
  imageUrl?: string
  sender: 'user' | 'ai' | 'expert' | 'system'
  timestamp: string
  questionId?: string
  status?: string
}

export interface ExpertReview {
  id: string
  questionId: string
  expertId: string
  aiResponse: string
  expertDecision: 'approved' | 'rejected'
  expertNotes?: string
  reviewedAt: string
}

export interface PendingReview {
  id: string
  questionId: string
  question: string
  subject: string
  aiResponse: string
  submittedAt: string
  userId: string
  userName: string
}

export interface APIResponse<T = any> {
  success: boolean
  message: string
  data?: T
  error?: string
}