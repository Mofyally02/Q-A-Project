<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">System Test</h1>
            <p class="mt-1 text-sm text-gray-500">Upload test questions to verify API keys and system functionality</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Test Form -->
      <div class="bg-white rounded-lg shadow mb-6">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Submit Test Question</h2>
          <p class="mt-1 text-sm text-gray-500">Upload a test question to verify that API keys are working correctly after updates</p>
        </div>
        <form @submit.prevent="submitTestQuestion" class="p-6 space-y-6">
          <!-- Subject -->
          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
              Subject <span class="text-red-500">*</span>
            </label>
            <input
              id="subject"
              v-model="formData.subject"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Mathematics, Physics, Chemistry"
            />
          </div>

          <!-- Question Content -->
          <div>
            <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
              Question <span class="text-red-500">*</span>
            </label>
            <textarea
              id="content"
              v-model="formData.content"
              required
              rows="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter your test question here..."
            ></textarea>
            <p class="mt-2 text-sm text-gray-500">This question will be processed through the system to test API connectivity</p>
          </div>

          <!-- Test Reason -->
          <div>
            <label for="testReason" class="block text-sm font-medium text-gray-700 mb-2">
              Test Reason (Optional)
            </label>
            <input
              id="testReason"
              v-model="formData.testReason"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Testing OpenAI API key after update"
            />
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <span v-if="isSubmitting">Submitting...</span>
              <span v-else>Submit Test Question</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Test Results -->
      <div v-if="testResults.length > 0" class="bg-white rounded-lg shadow">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Test Results</h2>
        </div>
        <div class="divide-y divide-gray-200">
          <div
            v-for="(result, index) in testResults"
            :key="index"
            class="p-6"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-md font-medium text-gray-900">{{ result.subject }}</h3>
                <p class="text-sm text-gray-500 mt-1">{{ result.content.substring(0, 100) }}...</p>
                <p class="text-xs text-gray-400 mt-2">Question ID: {{ result.questionId }}</p>
              </div>
              <div class="ml-4">
                <span
                  :class="{
                    'bg-green-100 text-green-800': result.systemStatus === 'healthy',
                    'bg-yellow-100 text-yellow-800': result.systemStatus === 'processing',
                    'bg-red-100 text-red-800': result.systemStatus === 'error',
                    'bg-gray-100 text-gray-800': result.systemStatus === 'pending'
                  }"
                  class="px-3 py-1 text-xs font-medium rounded-full"
                >
                  {{ result.status }}
                </span>
              </div>
            </div>

            <!-- Status Message -->
            <div
              :class="{
                'bg-green-50 border-green-200': result.systemStatus === 'healthy',
                'bg-yellow-50 border-yellow-200': result.systemStatus === 'processing',
                'bg-red-50 border-red-200': result.systemStatus === 'error',
                'bg-gray-50 border-gray-200': result.systemStatus === 'pending'
              }"
              class="p-4 rounded-lg border mb-4"
            >
              <p class="text-sm" :class="{
                'text-green-800': result.systemStatus === 'healthy',
                'text-yellow-800': result.systemStatus === 'processing',
                'text-red-800': result.systemStatus === 'error',
                'text-gray-800': result.systemStatus === 'pending'
              }">
                {{ result.message }}
              </p>
            </div>

            <!-- Additional Info -->
            <div v-if="result.confidenceScore !== null || result.aiContentPercentage !== null" class="grid grid-cols-2 gap-4 text-sm">
              <div v-if="result.confidenceScore !== null">
                <span class="text-gray-500">Confidence Score:</span>
                <span class="font-medium ml-2">{{ (result.confidenceScore * 100).toFixed(1) }}%</span>
              </div>
              <div v-if="result.aiContentPercentage !== null">
                <span class="text-gray-500">AI Content:</span>
                <span class="font-medium ml-2">{{ result.aiContentPercentage.toFixed(1) }}%</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="mt-4 flex gap-2">
              <button
                @click="checkStatus(result.questionId, index)"
                :disabled="result.isChecking"
                class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition"
              >
                <span v-if="result.isChecking">Checking...</span>
                <span v-else>Refresh Status</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-white rounded-lg shadow p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-4 text-sm font-medium text-gray-900">No test results yet</h3>
        <p class="mt-2 text-sm text-gray-500">Submit a test question above to verify system functionality</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from '~/composables/useApi'

// Page meta
definePageMeta({
  middleware: 'admin',
  layout: 'dashboard'
})

const api = useApi()
const formData = ref({
  subject: '',
  content: '',
  testReason: ''
})

const isSubmitting = ref(false)
const testResults = ref([])

const submitTestQuestion = async () => {
  if (!formData.value.subject || !formData.value.content) {
    alert('Please fill in all required fields')
    return
  }

  isSubmitting.value = true
  try {
    const result = await api.submitTestQuestion({
      content: formData.value.content,
      subject: formData.value.subject,
      type: 'text',
      test_reason: formData.value.testReason || 'API key verification'
    })

    if (result.success) {
      // Add to test results
      testResults.value.unshift({
        questionId: result.data.question_id,
        subject: formData.value.subject,
        content: formData.value.content,
        status: result.data.status,
        systemStatus: 'processing',
        message: result.data.message || 'Test question submitted successfully',
        confidenceScore: null,
        aiContentPercentage: null,
        isChecking: false
      })

      // Reset form
      formData.value = {
        subject: '',
        content: '',
        testReason: ''
      }

      // Auto-check status after 5 seconds
      setTimeout(() => {
        checkStatus(result.data.question_id, 0)
      }, 5000)
    } else {
      alert(`Failed to submit test question: ${result.message}`)
    }
  } catch (error) {
    console.error('Error submitting test question:', error)
    alert('Failed to submit test question. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const checkStatus = async (questionId, index) => {
  if (testResults.value[index]) {
    testResults.value[index].isChecking = true
  }

  try {
    const result = await api.getTestQuestionStatus(questionId)

    if (result.success && testResults.value[index]) {
      const data = result.data
      testResults.value[index].status = data.status
      testResults.value[index].systemStatus = data.system_status || 'pending'
      testResults.value[index].message = data.message || 'Status updated'
      testResults.value[index].confidenceScore = data.confidence_score
      testResults.value[index].aiContentPercentage = data.ai_content_percentage
    }
  } catch (error) {
    console.error('Error checking status:', error)
  } finally {
    if (testResults.value[index]) {
      testResults.value[index].isChecking = false
    }
  }
}
</script>

