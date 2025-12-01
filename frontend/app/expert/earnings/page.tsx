
'use client'

import { TrendingUp, Loader2, DollarSign, BarChart2, Clock, Star } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { Bar } from 'react-chartjs-2'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
    Legend
  } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

import { useAuthStore } from '@/app/client/lib/store'
import { apiHelpers } from '@/app/client/lib/api'
import { UserRole } from '@/types'

import { Button } from '@/app/client/components/ui/button'
import { cn } from '@/app/client/lib/utils'

export default function ExpertEarningsPage() {
  const router = useRouter()
//   const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [earningsData, setEarningsData] = useState<any>(null) // Replace with actual type

  // Mock user and apiHelpers
  const user = { role: 'expert', id: 'mock-expert-id' }
  const apiHelpers = {
    getExpertEarnings: async () => {
      // Simulate API call
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              success: true,
              data: {
                stats: {
                  total_reviews: 25,
                  approved_reviews: 20,
                  rated_reviews: 18,
                  average_rating: 4.7
                },
                earnings: {
                  total_earned: 200.00,
                  pending_payout: 50.00,
                  currency: 'USD'
                },
                weekly_earnings: [
                    { week: '2025-W44', reviews: 5, earnings: 50 },
                    { week: '2025-W45', reviews: 7, earnings: 70 },
                    { week: '2025-W46', reviews: 8, earnings: 80 },
                ],
                breakdown: [
                    { question_id: 'qc1', subject: 'Algebra Review', is_approved: true, review_date: new Date().toISOString(), overall_score: 4.5, amount: 10 },
                    { question_id: 'qc2', subject: 'Poetry Analysis', is_approved: true, review_date: new Date().toISOString(), overall_score: 5, amount: 10 },
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

    const fetchEarningsData = async () => {
      try {
        setLoading(true)
        const response: any = await apiHelpers.getExpertEarnings() // Assuming a getExpertEarnings API
        if (response.data.success) {
          setEarningsData(response.data.data)
        } else {
          toast.error(response.data.message || 'Failed to load earnings data.')
        }
      } catch (error) {
        toast.error('An error occurred while fetching earnings data.')
      } finally {
        setLoading(false)
      }
    }
    fetchEarningsData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const stats = earningsData?.stats || {}
  const earnings = earningsData?.earnings || {}
  const weeklyEarnings = earningsData?.weekly_earnings || []
  const breakdown = earningsData?.breakdown || []

  const chartData = {
    labels: weeklyEarnings.map((data: any) => data.week),
    datasets: [
      {
        label: 'Earnings',
        data: weeklyEarnings.map((data: any) => data.earnings),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };


  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      <div className="glass bg-card/60 p-4 sm:p-6 rounded-lg sm:rounded-lg shadow-soft flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="p-3 bg-primary/20 rounded-lg flex-shrink-0">
          <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">My Earnings</h1>
          <p className="text-muted-foreground mt-1 text-sm sm:text-base">Track your performance and payouts</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <DollarSign className="w-8 h-8 text-green-500" />
          <div>
            <p className="text-muted-foreground text-sm">Total Earned</p>
            <p className="text-foreground text-2xl font-semibold">{earnings.currency}{earnings.total_earned?.toFixed(2)}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Clock className="w-8 h-8 text-yellow-500" />
          <div>
            <p className="text-muted-foreground text-sm">Pending Payout</p>
            <p className="text-foreground text-2xl font-semibold">{earnings.currency}{earnings.pending_payout?.toFixed(2)}</p>
          </div>
        </div>
        <div className="glass bg-card/60 p-5 rounded-lg shadow-soft flex items-center space-x-4">
          <Star className="w-8 h-8 text-purple-500" />
          <div>
            <p className="text-muted-foreground text-sm">Average Rating</p>
            <p className="text-foreground text-2xl font-semibold">{stats.average_rating?.toFixed(1)}</p>
          </div>
        </div>
      </div>

      {/* Weekly Earnings Chart */}
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft">
        <h2 className="text-xl font-bold text-foreground mb-4">Weekly Earnings</h2>
        <Bar data={chartData} />
      </div>

      {/* Earnings Breakdown */}
      <div className="glass bg-card/60 p-6 rounded-lg shadow-soft">
        <h2 className="text-xl font-bold text-foreground mb-4">Earnings Breakdown</h2>
        {breakdown.length > 0 ? (
          <div className="space-y-4">
            {breakdown.map((item: any) => (
              <div
                key={item.question_id}
                className="flex items-center justify-between p-3 bg-background/50 rounded-lg shadow-sm"
              >
                <div>
                  <h3 className="font-semibold text-foreground">{item.subject}</h3>
                  <p className="text-muted-foreground text-sm">Reviewed: {new Date(item.review_date).toLocaleDateString()}</p>
                </div>
                <p className={`font-bold ${item.is_approved ? 'text-green-500' : 'text-destructive'}`}>
                  {earnings.currency}{item.amount?.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <BarChart2 className="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
            <p>No earnings data available yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
