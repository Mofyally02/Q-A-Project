export enum UserRole {
  CLIENT = 'client',
  EXPERT = 'expert',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
  ADMIN_EDITOR = 'admin_editor'
}

export enum QuestionType {
  TEXT = 'text',
  IMAGE = 'image'
}

export enum QuestionStatus {
  SUBMITTED = 'submitted',
  PROCESSING = 'processing',
  HUMANIZED = 'humanized',
  REVIEW = 'review',
  DELIVERED = 'delivered',
  RATED = 'rated'
}

export interface User {
  user_id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface Question {
  question_id: string
  client_id: string
  type: QuestionType
  content: Record<string, any>
  subject: string
  status: QuestionStatus
  created_at: string
}

export interface Answer {
  answer_id: string
  question_id: string
  expert_id?: string
  ai_response?: Record<string, any>
  humanized_response?: Record<string, any>
  expert_response?: Record<string, any>
  confidence_score?: number
  is_approved?: boolean
  rejection_reason?: string
  created_at: string
}

export interface Rating {
  rating_id: string
  question_id: string
  expert_id?: string
  score: number
  comment?: string
  created_at: string
}

export interface APIResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

export interface LoginResponse {
  success: boolean
  message: string
  access_token?: string
  token_type?: string
  user?: User
}

