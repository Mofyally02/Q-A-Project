'use client'

import { TrendingUp, Loader2, DollarSign } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'

import { Button } from '@/app/client/components/ui/button'
import { Card } from '@/components/ui/card'

export default function ClientWalletPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [walletData, setWalletData] = useState<any>(null)
  const [topUpAmount, setTopUpAmount] = useState<number>(10)

  useEffect(() => {
    hydrateApiAuth()
  }, [])

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== UserRole.CLIENT) {
      router.push('/auth')
      toast.error('Client access only')
      return
    }
    loadWallet()
  }, [user, isAuthenticated, router])

  const loadWallet = async () => {
    try {
      setLoading(true)
      const response: any = await apiHelpers.getWalletInfo()
      const data = response.data?.data || response.data
      setWalletData(data)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load wallet')
    } finally {
      setLoading(false)
    }
  }

  const handleTopup = async () => {
    if (topUpAmount <= 0) {
      toast.error('Please enter a valid amount')
      return
    }
    try {
      setLoading(true)
      const response: any = await apiHelpers.initiateTopup(topUpAmount)
      if (response.data?.success) {
        toast.success('Top-up initiated successfully')
        await loadWallet()
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to initiate top-up')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !walletData) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const transactions = walletData?.transactions || []
  const balance = walletData?.balance || walletData?.credits || 0

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Wallet</h1>
          <p className="text-muted-foreground mt-1">Manage your credits and view transactions</p>
        </div>
      </div>

      {/* Balance and Top Up Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Current Balance */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Current Balance</h2>
          <div className="flex items-center gap-4">
            <DollarSign className="w-8 h-8 text-green-500" />
            <p className="text-5xl font-extrabold text-foreground">
              ${balance.toFixed(2)}
            </p>
          </div>
        </Card>

        {/* Top Up */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Add Credits</h2>
          <div className="flex items-center gap-4">
            <input
              type="number"
              value={topUpAmount}
              onChange={(e) => setTopUpAmount(parseFloat(e.target.value) || 0)}
              min="1"
              step="1"
              className="flex-1 px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-primary"
            />
            <Button onClick={handleTopup} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Top Up'}
            </Button>
          </div>
          <p className="text-muted-foreground text-sm mt-2">Secure payments via Stripe/PayPal</p>
        </Card>
      </div>

      {/* Transaction History */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Transaction History</h2>
        {transactions.length > 0 ? (
          <div className="space-y-3">
            {transactions.map((tx: any) => (
              <div key={tx.id || tx.transaction_id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div>
                  <p className="font-semibold text-foreground capitalize">{tx.type || tx.transaction_type}</p>
                  <p className="text-muted-foreground text-sm">
                    {new Date(tx.created_at || tx.date).toLocaleDateString()}
                  </p>
                </div>
                <p className={`font-bold ${(tx.amount || tx.credit_amount || 0) > 0 ? 'text-green-500' : 'text-destructive'}`}>
                  {(tx.amount || tx.credit_amount || 0) > 0 ? '+' : ''}${Math.abs(tx.amount || tx.credit_amount || 0).toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-8">No transactions yet</p>
        )}
      </Card>
    </div>
  )
}
