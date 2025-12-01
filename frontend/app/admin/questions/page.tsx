'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ShoppingCart, Loader2, Search, Filter, Eye, Clock, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function AdminOrdersPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [orders, setOrders] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

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
    loadOrders()
  }, [user, router])

  const loadOrders = async () => {
    try {
      setLoading(true)
      // Use questions endpoint as orders
      const response = await apiHelpers.getQuestions({})
      if (response.data?.success) {
        setOrders(response.data.data?.questions || [])
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load orders')
    } finally {
      setLoading(false)
    }
  }

  const filteredOrders = orders.filter(order => {
    const matchesSearch = !searchQuery || 
      order.question_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.subject?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || order.status === filterStatus
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading orders...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Orders</h1>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search orders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">All Status</option>
            <option value="submitted">Submitted</option>
            <option value="processing">Processing</option>
            <option value="delivered">Delivered</option>
            <option value="rated">Rated</option>
          </select>
        </div>
      </Card>

      {/* Orders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredOrders.length > 0 ? (
          filteredOrders.map((order) => (
            <Card key={order.question_id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      {order.subject || `Order #${order.question_id?.slice(0, 8)}`}
                    </h3>
                    <Badge variant="outline" className="text-xs">
                      {order.status || 'Unknown'}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>ID: #{order.question_id?.slice(0, 8)}</p>
                  <p>Created: {new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <div className="pt-4 border-t border-border">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => router.push(`/admin/questions/${order.question_id}`)}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <ShoppingCart className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No orders found</p>
          </div>
        )}
      </div>
    </div>
  )
}

