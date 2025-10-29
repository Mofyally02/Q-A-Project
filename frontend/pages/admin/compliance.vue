<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Compliance</h1>
            <p class="mt-1 text-sm text-gray-500">Monitor compliance and generate reports</p>
          </div>
          <div class="flex gap-3">
            <button
              @click="generateReport"
              class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              Generate Report
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
      <!-- Compliance Status -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-green-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">GDPR Compliance</p>
              <p class="text-2xl font-bold text-gray-900">{{ complianceData?.status?.gdpr || 'Compliant' }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-blue-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Data Security</p>
              <p class="text-2xl font-bold text-gray-900">{{ complianceData?.status?.security || 'Secure' }}</p>
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
              <p class="text-sm font-medium text-gray-600">Audit Logs</p>
              <p class="text-2xl font-bold text-gray-900">{{ complianceData?.status?.audit_logs || 'Active' }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="bg-purple-100 rounded-lg p-3">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Reports Generated</p>
              <p class="text-2xl font-bold text-gray-900">{{ complianceData?.status?.reports || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Compliance Logs -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Recent Compliance Logs</h2>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div
              v-for="(log, index) in complianceData?.logs"
              :key="index"
              class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ log.event }}</p>
                <p class="text-sm text-gray-500">{{ log.description }}</p>
              </div>
              <div class="ml-4">
                <span
                  :class="{
                    'bg-green-100 text-green-800': log.status === 'compliant',
                    'bg-yellow-100 text-yellow-800': log.status === 'warning',
                    'bg-red-100 text-red-800': log.status === 'violation'
                  }"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ log.status }}
                </span>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(log.timestamp) }}</p>
              </div>
            </div>
            <div v-if="!complianceData?.logs?.length" class="text-center text-gray-500 py-8">
              No compliance logs available
            </div>
          </div>
        </div>
      </div>

      <!-- Compliance Reports -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Compliance Reports</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="border rounded-lg p-4">
              <h3 class="font-medium text-gray-900 mb-2">Data Protection Report</h3>
              <p class="text-sm text-gray-600 mb-3">Review data protection measures and GDPR compliance.</p>
              <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">Download PDF</button>
            </div>
            <div class="border rounded-lg p-4">
              <h3 class="font-medium text-gray-900 mb-2">Security Audit Report</h3>
              <p class="text-sm text-gray-600 mb-3">Comprehensive security audit and vulnerability assessment.</p>
              <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">Download PDF</button>
            </div>
            <div class="border rounded-lg p-4">
              <h3 class="font-medium text-gray-900 mb-2">User Access Report</h3>
              <p class="text-sm text-gray-600 mb-3">Track user access patterns and permissions.</p>
              <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">Download PDF</button>
            </div>
            <div class="border rounded-lg p-4">
              <h3 class="font-medium text-gray-900 mb-2">System Activity Report</h3>
              <p class="text-sm text-gray-600 mb-3">Monitor system activities and potential issues.</p>
              <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">Download PDF</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Page meta
definePageMeta({
  middleware: 'admin',
  layout: 'dashboard'
})

const complianceData = ref(null)
const loading = ref(false)

const fetchComplianceData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('auth_token')

    // Fetch audit logs
    const logsResponse = await fetch('http://localhost:8000/admin/compliance/logs', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    // Fetch flagged content
    const flaggedResponse = await fetch('http://localhost:8000/admin/compliance/flagged', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (logsResponse.ok && flaggedResponse.ok) {
      const logsResult = await logsResponse.json()
      const flaggedResult = await flaggedResponse.json()

      complianceData.value = {
        status: {
          gdpr: 'Compliant',
          security: 'Secure',
          audit_logs: 'Active',
          reports: logsResult.data.logs?.length || 0
        },
        logs: logsResult.data.logs?.slice(0, 10) || [],
        flagged_content: flaggedResult.data.flagged_content || []
      }
    } else {
      console.error('Failed to fetch compliance data')
    }
  } catch (error) {
    console.error('Error fetching compliance data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchComplianceData()
}

const generateReport = () => {
  // Implement report generation
  console.log('Generating compliance report...')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchComplianceData()
})
</script>
