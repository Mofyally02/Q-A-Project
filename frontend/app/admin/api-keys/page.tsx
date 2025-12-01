'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  KeySquare, 
  Loader2, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Plus,
  Eye,
  EyeOff,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'

const PROVIDERS = [
  'openai',
  'anthropic',
  'google',
  'xai',
  'stealth',
  'turnitin',
  'poe_chatgpt',
  'poe_claude'
]

type ApiKey = {
  key_id?: string
  provider: string
  status: 'configured' | 'missing' | 'invalid'
  last_4_chars?: string
  last_tested?: string
  test_result?: string
}

export default function AdminApiKeysPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [testingKey, setTestingKey] = useState<string | null>(null)
  const [addKeyDialog, setAddKeyDialog] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState('')
  const [newKeyValue, setNewKeyValue] = useState('')
  const [showKey, setShowKey] = useState<Record<string, boolean>>({})

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
    loadApiKeys()
  }, [user, router])

  const loadApiKeys = async () => {
    try {
      setLoading(true)
      const response = await apiHelpers.getApiKeys()
      const keys = response.data?.data?.keys || []
      
      // Ensure all providers are represented
      const allKeys = PROVIDERS.map(provider => {
        const existing = keys.find((k: ApiKey) => k.provider === provider)
        return existing || { provider, status: 'missing' as const }
      })
      
      setApiKeys(allKeys)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  const handleTestKey = async (provider: string) => {
    try {
      setTestingKey(provider)
      await apiHelpers.testApiKey(provider)
      toast.success(`${provider.toUpperCase()} key verified successfully`)
      await loadApiKeys()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || `Failed to verify ${provider}`)
    } finally {
      setTestingKey(null)
    }
  }

  const handleAddKey = async () => {
    if (!selectedProvider || !newKeyValue) {
      toast.error('Please select provider and enter key')
      return
    }
    
    try {
      await apiHelpers.addApiKey(selectedProvider, newKeyValue)
      toast.success('API key added successfully')
      setAddKeyDialog(false)
      setSelectedProvider('')
      setNewKeyValue('')
      await loadApiKeys()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to add API key')
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'configured':
        return <Badge variant="default" className="bg-success/20 text-success border-success/30">Configured</Badge>
      case 'invalid':
        return <Badge variant="error">Invalid</Badge>
      default:
        return <Badge variant="outline">Missing</Badge>
    }
  }

  if (loading && apiKeys.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading API keys...</p>
        </div>
      </div>
    )
  }

  const configuredCount = apiKeys.filter(k => k.status === 'configured').length
  const missingCount = apiKeys.filter(k => k.status === 'missing').length

  return (
    <div className="w-full space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 w-full">
        <div>
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground flex items-center gap-2 sm:gap-3">
            <KeySquare className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-primary" />
            API Key Management
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-1 sm:mt-2">
            Manage and test API keys for all integrated services
          </p>
        </div>
        <Dialog open={addKeyDialog} onOpenChange={setAddKeyDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Key
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add API Key</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground"
                >
                  <option value="">Select provider...</option>
                  {PROVIDERS.map(provider => (
                    <option key={provider} value={provider}>
                      {provider.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  API Key
                </label>
                <div className="relative">
                  <Input
                    type={showKey[selectedProvider] ? 'text' : 'password'}
                    value={newKeyValue}
                    onChange={(e) => setNewKeyValue(e.target.value)}
                    placeholder="Enter API key..."
                    className="pr-10 bg-background/50 border-border/50"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full"
                    onClick={() => setShowKey({ ...showKey, [selectedProvider]: !showKey[selectedProvider] })}
                  >
                    {showKey[selectedProvider] ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setAddKeyDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddKey}>
                  Add Key
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Providers</p>
              <p className="text-2xl font-bold text-foreground">{PROVIDERS.length}</p>
            </div>
            <KeySquare className="w-8 h-8 text-primary opacity-50" />
          </div>
        </Card>
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Configured</p>
              <p className="text-2xl font-bold text-success">{configuredCount}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-success opacity-50" />
          </div>
        </Card>
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Missing</p>
              <p className="text-2xl font-bold text-warning">{missingCount}</p>
            </div>
            <XCircle className="w-8 h-8 text-warning opacity-50" />
          </div>
        </Card>
      </div>

      {/* API Keys List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
        {apiKeys.map((key) => (
          <Card 
            key={key.provider} 
            className="glass border-border/50 p-4 sm:p-6 hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  key.status === 'configured' 
                    ? 'bg-success/10 text-success' 
                    : key.status === 'invalid'
                    ? 'bg-destructive/10 text-destructive'
                    : 'bg-muted text-muted-foreground'
                }`}>
                  {key.status === 'configured' ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <XCircle className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-foreground uppercase">{key.provider}</h3>
                  {getStatusBadge(key.status)}
                </div>
              </div>
            </div>
            
            {key.last_4_chars && (
              <div className="mb-3">
                <p className="text-xs text-muted-foreground mb-1">Key Preview</p>
                <p className="text-sm font-mono text-foreground/70">
                  •••• •••• •••• {key.last_4_chars}
                </p>
              </div>
            )}
            
            {key.last_tested && (
              <div className="mb-3">
                <p className="text-xs text-muted-foreground">
                  Last tested: {new Date(key.last_tested).toLocaleString()}
                </p>
              </div>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => handleTestKey(key.provider)}
              disabled={testingKey === key.provider || key.status === 'missing'}
              className="w-full"
            >
              {testingKey === key.provider ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Test Connection
                </>
              )}
            </Button>
          </Card>
        ))}
      </div>

      {/* Security Note */}
      <Card className="glass border-border/50 p-4 sm:p-6 bg-warning/5 border-warning/20">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-warning mt-0.5" />
          <div>
            <h4 className="font-semibold text-foreground mb-1">Security Note</h4>
            <p className="text-sm text-muted-foreground">
              API keys are encrypted server-side and audited on every change. Keep your VPN active when updating keys.
              Never share API keys or commit them to version control.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
