<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Analytics</h1>
            <p class="mt-1 text-sm text-gray-500">System analytics and insights</p>
          </div>
          <div class="flex gap-3">
            <button
              @click="exportData"
              class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              Export Data
            </button>
            <button
              @click="refreshData"
              class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Analytics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-blue-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Questions</p>
              <p class="text-2xl font-bold text-gray-900">{{ analyticsData?.stats?.total_questions || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-green-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Growth Rate</p>
              <p class="text-2xl font-bold text-gray-900">{{ analyticsData?.stats?.growth_rate || '0%' }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-yellow-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p class="text-2xl font-bold text-gray-900">{{ analyticsData?.stats?.avg_response_time || '0s' }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-purple-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">User Satisfaction</p>
              <p class="text-2xl font-bold text-gray-900">{{ analyticsData?.stats?.user_satisfaction || '0%' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Questions Over Time -->
        <div class="bg-white rounded-lg shadow">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Questions Over Time</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div
                v-for="(data, index) in analyticsData?.charts?.questions_over_time"
                :key="index"
                class="flex items-center justify-between"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ data.period }}</p>
                  <div class="mt-1 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-blue-600 h-2 rounded-full"
                      :style="{ width: `${(data.count / maxQuestionsCount) * 100}%` }"
                    ></div>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-semibold text-gray-900">{{ data.count }}</p>
                </div>
              </div>
              <div v-if="!analyticsData?.charts?.questions_over_time?.length" class="text-center text-gray-500 py-8">
                No data available
              </div>
            </div>
          </div>
        </div>

        <!-- Subject Distribution -->
        <div class="bg-white rounded-lg shadow">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Subject Distribution</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div
                v-for="(subject, index) in analyticsData?.charts?.subject_distribution"
                :key="index"
                class="flex items-center justify-between"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ subject.subject }}</p>
                  <div class="mt-1 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-600 h-2 rounded-full"
                      :style="{ width: `${(subject.count / maxSubjectCount) * 100}%` }"
                    ></div>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-semibold text-gray-900">{{ subject.count }}</p>
                </div>
              </div>
              <div v-if="!analyticsData?.charts?.subject_distribution?.length" class="text-center text-gray-500 py-8">
                No data available
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Insights -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Additional Insights</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="text-center p-4 border rounded-lg">
              <p class="text-sm text-gray-600">Peak Hours</p>
              <p class="text-lg font-bold text-gray-900">{{ analyticsData?.insights?.peak_hours || 'N/A' }}</p>
            </div>
            <div class="text-center p-4 border rounded-lg">
              <p class="text-sm text-gray-600">Top Expert</p>
              <p class="text-lg font-bold text-gray-900">{{ analyticsData?.insights?.top_expert || 'N/A' }}</p>
            </div>
            <div class="text-center p-4 border rounded-lg">
              <p class="text-sm text-gray-600">System Load</p>
              <p class="text-lg font-bold text-gray-900">{{ analyticsData?.insights?.system_load || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Page meta
definePageMeta({
  middleware: 'admin'
})

const analyticsData = ref(null)
const loading = ref(false)

const maxQuestionsCount = computed(() => {
  if (!analyticsData.value?.charts?.questions_over_time) return 1
  return Math.max(...analyticsData.value.charts.questions_over_time.map(d => d.count), 1)
})

const maxSubjectCount = computed(() => {
  if (!analyticsData.value?.charts?.subject_distribution) return 1
  return Math.max(...analyticsData.value.charts.subject_distribution.map(s => s.count), 1)
})

const fetchAnalyticsData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')

    // Fetch questions analytics
    const questionsResponse = await fetch('http://localhost:8000/admin/analytics/questions', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    // Fetch expert analytics
    const expertsResponse = await fetch('http://localhost:8000/admin/analytics/experts', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (questionsResponse.ok && expertsResponse.ok) {
      const questionsResult = await questionsResponse.json()
      const expertsResult = await expertsResponse.json()

      // Process questions data for charts
      const questions = questionsResult.data.questions || []
      const questionsOverTime = processQuestionsOverTime(questions)
      const subjectDistribution = processSubjectDistribution(questions)

      analyticsData.value = {
        stats: {
          total_questions: questions.length,
          growth_rate: calculateGrowthRate(questions),
          avg_response_time: calculateAvgResponseTime(questions),
          user_satisfaction: calculateUserSatisfaction(questions)
        },
        charts: {
          questions_over_time: questionsOverTime,
          subject_distribution: subjectDistribution
        },
        insights: {
          peak_hours: '9 AM - 11 AM',
          top_expert: expertsResult.data.experts?.[0]?.email || 'N/A',
          system_load: 'Normal'
        }
      }
    } else {
      console.error('Failed to fetch analytics data')
    }
  } catch (error) {
    console.error('Error fetching analytics data:', error)
  } finally {
    loading.value = false
  }
}

const processQuestionsOverTime = (questions) => {
  // Group questions by date
  const grouped = questions.reduce((acc, q) => {
    const date = new Date(q.created_at).toISOString().split('T')[0]
    acc[date] = (acc[date] || 0) + 1
    return acc
  }, {})

  return Object.entries(grouped).map(([date, count]) => ({
    period: date,
    count
  })).slice(-7) // Last 7 days
}

const processSubjectDistribution = (questions) => {
  const grouped = questions.reduce((acc, q) => {
    const subject = q.subject || 'Unknown'
    acc[subject] = (acc[subject] || 0) + 1
    return acc
  }, {})

  return Object.entries(grouped).map(([subject, count]) => ({
    subject,
    count
  })).sort((a, b) => b.count - a.count).slice(0, 5)
}

const calculateGrowthRate = (questions) => {
  if (questions.length < 2) return '0%'
  const recent = questions.slice(0, Math.floor(questions.length / 2))
  const older = questions.slice(Math.floor(questions.length / 2))
  const recentAvg = recent.length / (recent.length || 1)
  const olderAvg = older.length / (older.length || 1)
  const growth = ((recentAvg - olderAvg) / olderAvg) * 100
  return `${growth > 0 ? '+' : ''}${growth.toFixed(1)}%`
}

const calculateAvgResponseTime = (questions) => {
  // Mock calculation - in real app, calculate from timestamps
  return '2.3s'
}

const calculateUserSatisfaction = (questions) => {
  // Mock calculation - in real app, calculate from ratings
  return '94%'
}

const refreshData = () => {
  fetchAnalyticsData()
}

const exportData = () => {
  // Implement export functionality
  console.log('Exporting data...')
}

onMounted(() => {
  fetchAnalyticsData()
})
</script>
