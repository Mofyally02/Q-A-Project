'use client'

import { Star, Loader2, TrendingUp, HelpCircle, Inbox, Clock, Zap } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useRealTimeStore } from '@/stores/useRealTimeStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { LiveQuestionCard } from '../components/LiveQuestionCard'
import { RecentAnswerCard } from '../components/RecentAnswerCard'
import { QuickAskCard } from '../components/QuickAskCard'
import { AchievementsCard } from '../components/AchievementsCard'
import { RecommendedActions } from '../components/RecommendedActions'
import { useWebSocket } from '../hooks/useWebSocket'

// Stat Card Component
const StatCard = ({ icon: Icon, title, value, color, iconBgColor }: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  value: string | number
  color: string
  iconBgColor: string
}) => (
  <div className={cn(
    "glass bg-card/60 p-4 sm:p-5 lg:p-6 rounded-lg sm:rounded-lg shadow-soft",
    "flex items-center space-x-3 sm:space-x-4 transition-all duration-300",
    "hover:scale-[1.02] hover:shadow-lg active:scale-100"
  )}>
    <div className={cn("p-2.5 sm:p-3 lg:p-4 rounded-full flex-shrink-0", iconBgColor)}>
      <Icon className={cn("w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7", color)} />
    </div>
    <div className="min-w-0 flex-1">
      <p className="text-muted-foreground text-xs sm:text-sm lg:text-base truncate">{title}</p>
      <p className="text-foreground text-xl sm:text-2xl lg:text-3xl font-semibold truncate">{value}</p>
    </div>
  </div>
)

// Get time-based greeting
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function ClientDashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const {
    liveQuestions,
    recentAnswers,
    notifications,
    credits,
    addLiveQuestion,
    updateQuestionStatus,
    addRecentAnswer,
    setCredits
  } = useRealTimeStore()
  
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!hydrated) return

    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only.')
      return
    }

    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getClientDashboard()
        
        // Handle different response structures
        const responseData = response?.data || response
        const success = responseData?.success !== false // Default to true if not specified
        const data = responseData?.data || responseData
        
        if (success && data) {
          setDashboardData(data)
          
          // Update real-time store with initial data
          if (data.stats?.total_credits !== undefined) {
            setCredits(data.stats.total_credits)
          } else if (data.stats?.credits !== undefined) {
            setCredits(data.stats.credits)
          }
          
          // Initialize recent answers
          if (data.recent_answers && Array.isArray(data.recent_answers)) {
            data.recent_answers.forEach((answer: any) => {
              addRecentAnswer({
                id: answer.id || answer.question_id,
                question: answer.subject || answer.question,
                answer: answer.preview || answer.answer || '',
                expert: answer.expert_name || 'Expert',
                rating: answer.rating,
                subject: answer.subject || 'General',
                timestamp: answer.created_at || new Date().toISOString(),
                image: answer.image
              })
            })
          }
          
          // Initialize live questions
          if (data.active_questions && Array.isArray(data.active_questions)) {
            data.active_questions.forEach((q: any) => {
              addLiveQuestion({
                id: q.id || q.question_id,
                subject: q.subject || 'Question',
                status: q.status === 'review' ? 'reviewing' : 'processing',
                timestamp: q.created_at || new Date().toISOString(),
                preview: q.preview
              })
            })
          }
        } else {
          const errorMessage = responseData?.message || responseData?.detail || 'Failed to load dashboard'
          toast.error(errorMessage)
          console.error('Dashboard fetch error:', responseData)
        }
      } catch (error: any) {
        // Extract error message from various possible locations
        let errorMessage = 'An error occurred while fetching dashboard data.'
        let errorDetails: any = {}
        
        if (error?.response) {
          // Axios error response
          errorMessage = error.response.data?.detail || 
                        error.response.data?.message || 
                        error.response.statusText ||
                        `HTTP ${error.response.status}: ${error.response.statusText}`
          errorDetails = {
            status: error.response.status,
            statusText: error.response.statusText,
            data: error.response.data,
            url: error.config?.url,
            method: error.config?.method
          }
        } else if (error?.message) {
          // Standard error message
          errorMessage = error.message
          errorDetails = {
            message: error.message,
            name: error.name,
            stack: error.stack
          }
        } else {
          // Unknown error - try to extract what we can
          errorDetails = {
            errorType: typeof error,
            errorString: String(error),
            errorKeys: Object.keys(error || {})
          }
        }
        
        // Show user-friendly error message
        toast.error(errorMessage)
        
        // Log error details for debugging (avoid logging empty objects)
        if (Object.keys(errorDetails).length > 0) {
          console.error('Dashboard fetch error:', errorMessage, errorDetails)
        } else {
          console.error('Dashboard fetch error:', errorMessage, 'No additional details available')
        }
        
        // Set default/empty data to prevent page crash
        setDashboardData({
          stats: {
            questions_asked: 0,
            avg_rating_given: 0,
            pending_answers: 0,
            total_credits: 0
          },
          recent_answers: [],
          active_questions: []
        })
      } finally {
        setLoading(false)
      }
    }
    fetchDashboardData()
  }, [hydrated, user, isAuthenticated, router])

  // WebSocket connection for real-time updates
  // Only connect if user is authenticated
  const wsUrl = isAuthenticated && user
    ? (process.env.NEXT_PUBLIC_WS_URL 
        ? `${process.env.NEXT_PUBLIC_WS_URL.replace(/\/$/, '')}/ws/client`
        : typeof window !== 'undefined'
        ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:8000/ws/client`
        : undefined)
    : undefined
  useWebSocket(wsUrl)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    )
  }

  const stats = dashboardData?.stats || {}
  const greeting = getGreeting()
  const questionsThisMonth = stats.questions_asked || 0

  return (
    <div className="w-full space-y-6 animate-fade-in">
      {/* Personal Greeting */}
      <div className={cn(
        "bg-gradient-to-br from-primary/80 via-purple-500/80 to-pink-500/80",
        "p-4 sm:p-6 lg:p-8 rounded-lg sm:rounded-lg shadow-lg text-white"
      )}>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
          {greeting}, {user?.first_name || 'Client'}!
        </h1>
        <p className="opacity-90 mt-1 sm:mt-2 text-sm sm:text-base">
          {questionsThisMonth > 0 
            ? `You've asked ${questionsThisMonth} question${questionsThisMonth > 1 ? 's' : ''} this month`
            : 'Ready for your next breakthrough question?'}
        </p>
      </div>

      {/* Key Metrics (4 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        <StatCard 
          icon={Star} 
          title="Avg. Rating Given" 
          value={stats.avg_rating_given || 'N/A'} 
          color="text-yellow-400" 
          iconBgColor="bg-yellow-500/10" 
        />
        <StatCard 
          icon={Zap} 
          title="Active Questions" 
          value={liveQuestions.filter(q => q.status !== 'delivered').length} 
          color="text-blue-400" 
          iconBgColor="bg-blue-500/10" 
        />
        <StatCard 
          icon={Inbox} 
          title="Pending Answers" 
          value={stats.pending_answers || 0} 
          color="text-purple-400" 
          iconBgColor="bg-purple-500/10" 
        />
        <StatCard 
          icon={TrendingUp} 
          title="Questions This Month" 
          value={questionsThisMonth} 
          color="text-green-400" 
          iconBgColor="bg-green-500/10" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Left Column - Quick Ask & Live Status */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6 flex flex-col">
          {/* Quick Ask Card - Same height as Achievements */}
          <div className="flex-1">
            <QuickAskCard />
          </div>

          {/* Live Status Panel */}
          {liveQuestions.length > 0 && (
            <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg sm:text-xl font-bold text-foreground flex items-center gap-2">
                  <Clock className="w-5 h-5 text-primary" />
                  Active Questions
                </h2>
                <span className="text-sm text-muted-foreground">
                  {liveQuestions.filter(q => q.status !== 'delivered').length} active
                </span>
              </div>
              <div className="space-y-3">
                {liveQuestions
                  .filter(q => q.status !== 'delivered')
                  .slice(0, 5)
                  .map((question) => (
                    <LiveQuestionCard key={question.id} question={question} />
                  ))}
              </div>
            </div>
          )}

          {/* Recent Answers Carousel - Same height as Recommended Actions */}
          <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft h-full flex flex-col">
            <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4 flex items-center gap-2">
              <Inbox className="w-5 h-5 text-primary" />
              Recent Answers
            </h2>
            <div className="flex-1 overflow-y-auto">
              {recentAnswers.length > 0 ? (
                <div className="space-y-3 sm:space-y-4">
                  {recentAnswers.slice(0, 5).map((answer) => (
                    <RecentAnswerCard key={answer.id} answer={answer} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 sm:py-12">
                  <Inbox className="w-12 h-12 sm:w-16 sm:h-16 mx-auto text-muted-foreground" />
                  <h3 className="mt-4 text-base sm:text-lg font-semibold text-foreground">No recent answers</h3>
                  <p className="mt-2 text-sm text-muted-foreground">Your answers will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Achievements & Actions */}
        <div className="space-y-4 sm:space-y-6 flex flex-col">
          {/* Achievements & Streaks - Same height as Quick Ask */}
          <div className="flex-1">
            <AchievementsCard
              streak={7}
              totalQuestions={questionsThisMonth}
              level="Gold"
              avgRating={parseFloat(stats.avg_rating_given) || 4.9}
            />
          </div>

          {/* Recommended Actions - Same height as Recent Answers */}
          <div className="flex-1">
            <RecommendedActions credits={credits} />
          </div>
        </div>
      </div>
    </div>
  )
}
