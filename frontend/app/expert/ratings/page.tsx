
'use client'

import { Star, Loader2, Award } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { cn } from '@/app/client/lib/utils'

export default function ExpertRatingsPage() {
  const router = useRouter()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [ratingsData, setRatingsData] = useState<any>(null) // Replace with actual type

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getExpertRatings: async () => {
      // Simulate API call
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                average_rating: 4.7,
                total_ratings: 18,
                leaderboard_position: 5,
                ratings: [
                  { id: 'r1', overall_score: 5, comment: 'Excellent and very detailed answer!', client_email: 'client1@example.com', created_at: new Date().toISOString(), question_subject: 'Algebra' },
                  { id: 'r2', overall_score: 4, comment: 'Good answer, but could be clearer.', client_email: 'client2@example.com', created_at: new Date().toISOString(), question_subject: 'Physics' },
                ]
              }
            }
          })
        }, 800)
      })
    }
  }

  useEffect(() => {
    // if (!user || user.role !== UserRole.EXPERT) {
    //   router.push('/login')
    //   toast.error('Expert access only.')
    //   return
    // }

    const fetchRatingsData = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getExpertRatings() // Assuming a getExpertRatings API
        if (response.data.success) {
          setRatingsData(response.data.data)
        } else {
          toast.error(response.data.message || 'Failed to load ratings data.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching ratings data.')
      } finally {
        setLoading(false)
      }
    }
    fetchRatingsData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const ratings = ratingsData?.ratings || []

  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft flex items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg">
          <Star className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Ratings</h1>
          <p className="text-muted-foreground mt-1">Feedback from clients and your performance</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Star className="w-8 h-8 text-yellow-500" />
          <div>
            <p className="text-muted-foreground text-sm">Average Rating</p>
            <p className="text-foreground text-2xl font-semibold">{ratingsData?.average_rating?.toFixed(1) || 'N/A'}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Award className="w-8 h-8 text-blue-500" />
          <div>
            <p className="text-muted-foreground text-sm">Total Ratings</p>
            <p className="text-foreground text-2xl font-semibold">{ratingsData?.total_ratings}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Award className="w-8 h-8 text-purple-500" />
          <div>
            <p className="text-muted-foreground text-sm">Leaderboard Position</p>
            <p className="text-foreground text-2xl font-semibold">{ratingsData?.leaderboard_position || 'N/A'}</p>
          </div>
        </div>
      </div>

      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft">
        <h2 className="text-xl font-bold text-foreground mb-4">Client Feedback</h2>
        {ratings.length > 0 ? (
          <div className="space-y-4">
            {ratings.map((rating: any) => (
              <div
                key={rating.id}
                className="p-4 bg-background/50 rounded-lg shadow-sm"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-foreground">{rating.question_subject}</h3>
                  <div className="flex items-center gap-1 text-yellow-500">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={cn("w-4 h-4", i < rating.overall_score ? 'fill-yellow-500' : 'fill-gray-300 text-gray-300')} />
                    ))}
                  </div>
                </div>
                <p className="text-muted-foreground text-sm">{rating.comment}</p>
                <p className="text-xs text-muted-foreground mt-2 opacity-75">
                  By {rating.client_email} on {new Date(rating.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Star className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
            <p>No ratings received yet.</p>
          </div>
        )}
      </div>
      </div>
    </div>
  )
}
