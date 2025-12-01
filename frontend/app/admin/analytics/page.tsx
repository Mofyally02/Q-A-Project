'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'

// Dynamically import Chart.js components to reduce initial bundle size
const Bar = dynamic(() => import('react-chartjs-2').then(mod => mod.Bar), {
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-muted rounded-lg" />
})
const Line = dynamic(() => import('react-chartjs-2').then(mod => mod.Line), {
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-muted rounded-lg" />
})
const Doughnut = dynamic(() => import('react-chartjs-2').then(mod => mod.Doughnut), {
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-muted rounded-lg" />
})

// Import shared chart registration
import { registerCharts } from '@/lib/chart-registry'
import {
  BarChart3,
  TrendingUp,
  Users,
  Activity,
  Loader2,
  Calendar,
  Download,
  Clock
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { ChartCard, StatCard } from '@/components/admin'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function AdminAnalyticsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [analytics, setAnalytics] = useState<any>(null)
  const [dateRange, setDateRange] = useState({ start: '', end: '' })

  useEffect(() => {
    hydrateApiAuth()
    // Register Chart.js on mount
    registerCharts()
  }, [])

  useEffect(() => {
    if (!user) return
    const isAdmin = user.role === UserRole.ADMIN || 
                   user.role === UserRole.SUPER_ADMIN || 
                   user.role === UserRole.ADMIN_EDITOR ||
                   user.email === 'allansaiti02@gmail.com'
    if (!isAdmin) {
      toast.error('Admin access only')
      router.replace('/admin/dashboard')
      return
    }
    loadAnalytics()
  }, [user, router])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const [questionsRes, expertsRes] = await Promise.all([
        apiHelpers.getAdminQuestionsAnalytics({
          start_date: dateRange.start || undefined,
          end_date: dateRange.end || undefined
        }),
        apiHelpers.getAdminExpertAnalytics()
      ])
      
      setAnalytics({
        questions: questionsRes.data?.data || {},
        experts: expertsRes.data?.data || {}
      })
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (dateRange.start || dateRange.end) {
      loadAnalytics()
    }
  }, [dateRange])

  if (loading && !analytics) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  const questionsData = analytics?.questions || {}
  const expertsData = analytics?.experts || {}

  return (
    <div className="w-full space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 w-full">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary" />
            Analytics & Insights
          </h1>
          <p className="text-muted-foreground mt-2">
            Platform performance metrics and data insights
          </p>
        </div>
        <div className="flex gap-2">
          <Input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            className="bg-background/50 border-border/50"
          />
          <Input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            className="bg-background/50 border-border/50"
          />
          <Button variant="outline" onClick={() => loadAnalytics()}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Questions"
          value={questionsData.total || 0}
          icon={Activity}
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="Active Experts"
          value={expertsData.active_count || 0}
          icon={Users}
          trend={{ value: 5, isPositive: true }}
        />
        <StatCard
          title="Avg Response Time"
          value={`${questionsData.avg_response_time || 0}h`}
          icon={Clock}
          trend={{ value: -10, isPositive: true }}
        />
        <StatCard
          title="Success Rate"
          value={`${questionsData.success_rate || 0}%`}
          icon={TrendingUp}
          trend={{ value: 3, isPositive: true }}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Questions Over Time"
          subtitle="Daily question volume"
        >
          <Line
            data={{
              labels: questionsData.daily_stats?.map((d: any) => d.date) || [],
              datasets: [{
                label: 'Questions',
                data: questionsData.daily_stats?.map((d: any) => d.count) || [],
                borderColor: 'hsl(var(--primary))',
                backgroundColor: 'hsla(var(--primary), 0.1)',
                tension: 0.4,
                fill: true
              }]
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false }
              }
            }}
          />
        </ChartCard>

        <ChartCard
          title="Status Distribution"
          subtitle="Questions by status"
        >
          <Doughnut
            data={{
              labels: questionsData.status_distribution?.map((s: any) => s.status) || [],
              datasets: [{
                data: questionsData.status_distribution?.map((s: any) => s.count) || [],
                backgroundColor: [
                  'hsl(var(--primary))',
                  'hsl(var(--accent))',
                  'hsl(var(--success))',
                  'hsl(var(--warning))'
                ]
              }]
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false
            }}
          />
        </ChartCard>
      </div>

      {/* Expert Performance */}
      <Card className="glass border-border/50 p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Top Performing Experts</h3>
        <div className="space-y-3">
          {expertsData.top_performers?.slice(0, 5).map((expert: any, idx: number) => (
            <div
              key={idx}
              className="flex items-center justify-between p-4 rounded-lg bg-background/50 border border-border/30"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Users className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium text-foreground">{expert.email}</p>
                  <p className="text-sm text-muted-foreground">
                    {expert.completed_count} completed • {expert.avg_rating?.toFixed(1)} rating
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-foreground">{expert.total_earnings || 0} credits</p>
                <p className="text-sm text-muted-foreground">Total earnings</p>
              </div>
            </div>
          )) || (
            <p className="text-center text-muted-foreground py-8">No expert data available</p>
          )}
        </div>
      </Card>
    </div>
  )
}
