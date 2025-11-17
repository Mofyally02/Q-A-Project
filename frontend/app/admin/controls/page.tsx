'use client'

import { useState, useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { apiHelpers } from '@/lib/api'
import { Search, Download, Users, Activity, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminControlsPage() {
  const { user, hasRole } = useAuthStore()
  const [questionSearchId, setQuestionSearchId] = useState('')
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null)
  const [experts, setExperts] = useState<any[]>([])
  const [reassignExpertId, setReassignExpertId] = useState('')
  const [reassignReason, setReassignReason] = useState('')
  const [approveReason, setApproveReason] = useState('')
  
  const [exportDataType, setExportDataType] = useState('questions')
  const [exportDays, setExportDays] = useState(30)
  const [exportResult, setExportResult] = useState<any>(null)
  
  const [expertPerformance, setExpertPerformance] = useState<any[]>([])
  const [systemHealth, setSystemHealth] = useState<any>(null)
  const [churnRisk, setChurnRisk] = useState<any[]>([])

  // Redirect if not admin
  useEffect(() => {
    if (user && !hasRole('admin' as any)) {
      window.location.href = '/dashboard'
    }
  }, [user, hasRole])

  useEffect(() => {
    fetchExperts()
    fetchAnalytics()
  }, [])

  const searchQuestion = async () => {
    if (!questionSearchId) {
      toast.error('Please enter a question ID')
      return
    }
    
    try {
      const response = await apiHelpers.getQuestionStatus(questionSearchId)
      if (response.data.success) {
        setSelectedQuestion(response.data.data)
      } else {
        toast.error(response.data.message || 'Question not found')
      }
    } catch (error: any) {
      toast.error('Error searching question')
    }
  }

  const fetchExperts = async () => {
    try {
      const response = await apiHelpers.getUsers()
      if (response.data.success) {
        setExperts(response.data.data.filter((u: any) => u.role === 'expert'))
      }
    } catch (error) {
      console.error('Error fetching experts:', error)
    }
  }

  const performReassign = async () => {
    if (!selectedQuestion || !reassignExpertId || !reassignReason) {
      toast.error('Please fill in all fields')
      return
    }
    
    try {
      const response = await apiHelpers.adminOverride(selectedQuestion.question_id, {
        action: 'reassign',
        expert_id: reassignExpertId,
        reason: reassignReason
      })
      
      if (response.data.success) {
        toast.success('Question reassigned successfully')
        setReassignExpertId('')
        setReassignReason('')
        await searchQuestion()
      } else {
        toast.error(response.data.message || 'Failed to reassign question')
      }
    } catch (error: any) {
      toast.error('Error reassigning question')
    }
  }

  const performApprove = async () => {
    if (!selectedQuestion || !approveReason) {
      toast.error('Please provide a reason')
      return
    }
    
    try {
      const response = await apiHelpers.adminOverride(selectedQuestion.question_id, {
        action: 'approve',
        reason: approveReason
      })
      
      if (response.data.success) {
        toast.success('Answer approved successfully')
        setApproveReason('')
        await searchQuestion()
      } else {
        toast.error(response.data.message || 'Failed to approve answer')
      }
    } catch (error: any) {
      toast.error('Error approving answer')
    }
  }

  const exportData = async () => {
    try {
      const response = await apiHelpers.exportData(exportDataType, exportDays)
      if (response.data.success) {
        setExportResult(response.data.data)
        toast.success(`Exported ${response.data.data.count} records`)
      } else {
        toast.error(response.data.message || 'Failed to export data')
      }
    } catch (error: any) {
      toast.error('Error exporting data')
    }
  }

  const downloadExport = () => {
    if (!exportResult) return
    
    const dataStr = JSON.stringify(exportResult.data, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${exportDataType}_export_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const fetchAnalytics = async () => {
    try {
      const response = await apiHelpers.getAdminAnalytics(30)
      if (response.data.success && response.data.data) {
        setExpertPerformance(response.data.data.expert_performance?.expert_performance || [])
        setSystemHealth(response.data.data.system_health || {})
        setChurnRisk(response.data.data.churn_risk_analysis?.at_risk_clients || [])
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Admin Controls</h1>
          <p className="mt-1 text-sm text-gray-500">Manage questions, experts, and system operations</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Question Override Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Question Override Controls</h2>
            <p className="mt-1 text-sm text-gray-500">Reassign questions or approve answers manually</p>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Question by ID
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={questionSearchId}
                  onChange={(e) => setQuestionSearchId(e.target.value)}
                  placeholder="Enter question ID"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={searchQuestion}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Search className="w-5 h-5" />
                </button>
              </div>
            </div>

            {selectedQuestion && (
              <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Question Details</h3>
                    <p className="text-xs text-gray-500">ID: {selectedQuestion.question_id}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    selectedQuestion.status === 'submitted' ? 'bg-yellow-100 text-yellow-800' :
                    selectedQuestion.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    selectedQuestion.status === 'delivered' ? 'bg-green-100 text-green-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {selectedQuestion.status}
                  </span>
                </div>

                <div className="space-y-2 text-sm mb-4">
                  <p><span className="font-medium">Subject:</span> {selectedQuestion.subject}</p>
                  <p><span className="font-medium">Type:</span> {selectedQuestion.type}</p>
                  <p><span className="font-medium">Created:</span> {new Date(selectedQuestion.created_at).toLocaleString()}</p>
                </div>

                <div className="pt-4 border-t border-gray-200 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reassign to Expert
                    </label>
                    <div className="flex gap-2">
                      <select
                        value={reassignExpertId}
                        onChange={(e) => setReassignExpertId(e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="">Select Expert</option>
                        {experts.map((expert) => (
                          <option key={expert.user_id} value={expert.user_id}>
                            {expert.first_name} {expert.last_name} ({expert.email})
                          </option>
                        ))}
                      </select>
                      <input
                        type="text"
                        value={reassignReason}
                        onChange={(e) => setReassignReason(e.target.value)}
                        placeholder="Reason for reassignment"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <button
                        onClick={performReassign}
                        disabled={!reassignExpertId || !reassignReason}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
                      >
                        Reassign
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Approve Answer
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={approveReason}
                        onChange={(e) => setApproveReason(e.target.value)}
                        placeholder="Reason for approval"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <button
                        onClick={performApprove}
                        disabled={!approveReason}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        Approve
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Data Export Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Data Export</h2>
            <p className="mt-1 text-sm text-gray-500">Export system data for analysis</p>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center gap-4">
              <select
                value={exportDataType}
                onChange={(e) => setExportDataType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="questions">Questions</option>
                <option value="ratings">Ratings</option>
                <option value="audit_logs">Audit Logs</option>
              </select>
              
              <input
                type="number"
                value={exportDays}
                onChange={(e) => setExportDays(Number(e.target.value))}
                min="1"
                max="365"
                className="w-24 px-4 py-2 border border-gray-300 rounded-lg"
              />
              
              <button
                onClick={exportData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export Data
              </button>
            </div>
            
            {exportResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  Export completed: {exportResult.count} records exported
                </p>
                <button
                  onClick={downloadExport}
                  className="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm"
                >
                  Download JSON
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Expert Performance */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Expert Performance
            </h2>
          </div>
          <div className="p-6">
            {expertPerformance.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expert</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Rating</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Ratings</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Approval Rate</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {expertPerformance.map((expert) => (
                      <tr key={expert.expert_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {expert.expert_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {expert.avg_rating?.toFixed(2) || '0.00'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {expert.total_ratings || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {expert.approval_rate?.toFixed(1) || '0.0'}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No expert performance data available</p>
            )}
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              System Health
            </h2>
          </div>
          <div className="p-6">
            {systemHealth && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-600">Uptime</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {systemHealth.uptime_percentage?.toFixed(1) || '0.0'}%
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm font-medium text-green-600">Avg Processing</p>
                  <p className="text-2xl font-bold text-green-900">
                    {systemHealth.processing_times?.avg_seconds?.toFixed(1) || '0.0'}s
                  </p>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm font-medium text-yellow-600">Error Rate</p>
                  <p className="text-2xl font-bold text-yellow-900">
                    {systemHealth.error_rate?.toFixed(2) || '0.00'}%
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm font-medium text-purple-600">Queue Health</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {systemHealth.queue_health ? 'Healthy' : 'N/A'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Churn Risk */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Churn Risk Analysis
            </h2>
          </div>
          <div className="p-6">
            {churnRisk.length > 0 ? (
              <div className="space-y-3">
                {churnRisk.map((client) => (
                  <div key={client.client_id} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">Client ID: {client.client_id}</p>
                        <p className="text-xs text-gray-500">Risk Type: {client.risk_type}</p>
                        <p className="text-xs text-gray-500">Risk Score: {(client.risk_score * 100).toFixed(1)}%</p>
                      </div>
                      <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No clients at risk identified</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

