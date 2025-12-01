'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  ShieldCheck, 
  Loader2, 
  AlertTriangle, 
  FileText,
  Download,
  Filter,
  Search,
  Calendar,
  User
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { DataTable, StatCard } from '@/components/admin'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function AdminCompliancePage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [auditLogs, setAuditLogs] = useState<any[]>([])
  const [flaggedContent, setFlaggedContent] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [dateFilter, setDateFilter] = useState({ start: '', end: '' })
  const [activeTab, setActiveTab] = useState('flagged')

  useEffect(() => {
    hydrateApiAuth()
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
    loadComplianceData()
  }, [user, router])

  const loadComplianceData = async () => {
    try {
      setLoading(true)
      const [auditRes, flaggedRes] = await Promise.all([
        apiHelpers.getAuditLogs({ 
          limit: 100,
          start_date: dateFilter.start || undefined,
          end_date: dateFilter.end || undefined
        }),
        apiHelpers.getFlaggedContent()
      ])
      setAuditLogs(auditRes.data?.data?.logs ?? [])
      setFlaggedContent(flaggedRes.data?.data?.flagged_content ?? [])
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load compliance data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (dateFilter.start || dateFilter.end) {
      loadComplianceData()
    }
  }, [dateFilter])

  const handleExport = () => {
    toast.success('Exporting compliance data...')
    // Implement export functionality
  }

  const filteredAuditLogs = auditLogs.filter(log => {
    if (!searchQuery) return true
    return (
      log.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.user_email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource_type?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  const filteredFlagged = flaggedContent.filter(item => {
    if (!searchQuery) return true
    return (
      item.question_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.subject?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  if (loading && auditLogs.length === 0 && flaggedContent.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading compliance data...</p>
        </div>
      </div>
    )
  }

  const auditLogColumns = [
    {
      key: 'action',
      header: 'Action',
      render: (log: any) => (
        <div>
          <p className="font-medium text-foreground">{log.action}</p>
          {log.resource_type && (
            <p className="text-xs text-muted-foreground">Type: {log.resource_type}</p>
          )}
        </div>
      ),
      sortable: true
    },
    {
      key: 'user_email',
      header: 'User',
      render: (log: any) => (
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-foreground">{log.user_email || 'System'}</span>
        </div>
      ),
      sortable: true
    },
    {
      key: 'created_at',
      header: 'Timestamp',
      render: (log: any) => (
        <div className="text-sm text-muted-foreground">
          {new Date(log.created_at).toLocaleString()}
        </div>
      ),
      sortable: true
    }
  ]

  const flaggedColumns = [
    {
      key: 'question_id',
      header: 'Question',
      render: (item: any) => (
        <div>
          <p className="font-medium text-foreground">{item.subject || 'Untitled'}</p>
          <p className="text-xs text-muted-foreground">ID: {item.question_id}</p>
        </div>
      ),
      sortable: true
    },
    {
      key: 'ai_content_percentage',
      header: 'AI Content',
      render: (item: any) => (
        <Badge variant={item.ai_content_percentage > 20 ? 'error' : 'warning'}>
          {item.ai_content_percentage?.toFixed(1) || 0}%
        </Badge>
      ),
      sortable: true
    },
    {
      key: 'created_at',
      header: 'Flagged',
      render: (item: any) => (
        <div className="text-sm text-muted-foreground">
          {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
        </div>
      ),
      sortable: true
    }
  ]

  return (
    <div className="w-full space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 w-full">
        <div>
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground flex items-center gap-2 sm:gap-3">
            <ShieldCheck className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-primary" />
            Compliance & Audit
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-1 sm:mt-2">
            Monitor flagged content and audit system actions
          </p>
        </div>
        <Button variant="outline" onClick={handleExport}>
          <Download className="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <StatCard
          title="Flagged Content"
          value={flaggedContent.length}
          icon={AlertTriangle}
          iconColor="text-warning"
          subtitle="Requires review"
        />
        <StatCard
          title="Audit Events"
          value={auditLogs.length}
          icon={FileText}
          iconColor="text-info"
          subtitle="Total logged actions"
        />
        <StatCard
          title="Compliance Rate"
          value={`${flaggedContent.length > 0 ? ((auditLogs.length - flaggedContent.length) / auditLogs.length * 100).toFixed(1) : 100}%`}
          icon={ShieldCheck}
          iconColor="text-success"
          subtitle="System compliance"
        />
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4 sm:space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="flagged">Flagged Content</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
        </TabsList>

        {/* Flagged Content Tab */}
        <TabsContent value="flagged" className="space-y-4">
          <Card className="glass border-border/50 p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Search flagged content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-background/50 border-border/50"
                />
              </div>
            </div>
            <DataTable
              data={filteredFlagged}
              columns={flaggedColumns}
              searchable={false}
              pagination={true}
              pageSize={10}
            />
          </Card>
        </TabsContent>

        {/* Audit Logs Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card className="glass border-border/50 p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Search audit logs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-background/50 border-border/50"
                />
              </div>
              <div className="flex gap-2">
                <Input
                  type="date"
                  value={dateFilter.start}
                  onChange={(e) => setDateFilter({ ...dateFilter, start: e.target.value })}
                  placeholder="Start date"
                  className="bg-background/50 border-border/50"
                />
                <Input
                  type="date"
                  value={dateFilter.end}
                  onChange={(e) => setDateFilter({ ...dateFilter, end: e.target.value })}
                  placeholder="End date"
                  className="bg-background/50 border-border/50"
                />
              </div>
            </div>
            <DataTable
              data={filteredAuditLogs}
              columns={auditLogColumns}
              searchable={false}
              pagination={true}
              pageSize={10}
            />
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
