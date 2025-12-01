'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Users, 
  Search, 
  Filter, 
  MoreVertical, 
  Ban, 
  CheckCircle, 
  UserPlus,
  Shield,
  UserCheck,
  Mail,
  Calendar,
  Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { apiHelpers, hydrateApiAuth } from '@/app/client/lib/api'
import { DataTable } from '@/components/admin'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

type User = {
  user_id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  last_login?: string
}

export default function AdminUsersPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [users, setUsers] = useState<User[]>([])
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [promoteDialogOpen, setPromoteDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

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
    loadUsers()
  }, [user, router])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const response = await apiHelpers.getUsers({
        role: selectedRole !== 'all' ? selectedRole : undefined,
        is_active: selectedStatus !== 'all' ? selectedStatus === 'active' : undefined
      })
      if (response.data?.success) {
        setUsers(response.data.data?.users || [])
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [selectedRole, selectedStatus])

  const handleBanUser = async (userId: string, ban: boolean) => {
    try {
      await apiHelpers.banUser(userId, ban)
      toast.success(ban ? 'User banned successfully' : 'User unbanned successfully')
      loadUsers()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to update user')
    }
  }

  const handlePromoteToExpert = async (userId: string) => {
    try {
      await apiHelpers.promoteToExpert(userId)
      toast.success('User promoted to expert')
      setPromoteDialogOpen(false)
      loadUsers()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to promote user')
    }
  }

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await apiHelpers.changeUserRole(userId, newRole)
      toast.success('User role updated')
      loadUsers()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to update role')
    }
  }

  const filteredUsers = users.filter(u => {
    const matchesSearch = !searchQuery || 
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `${u.first_name} ${u.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  const roleBadgeVariant = (role: UserRole): 'default' | 'secondary' | 'success' | 'warning' | 'info' | 'outline' | 'error' => {
    switch (role) {
      case UserRole.SUPER_ADMIN:
        return 'error'
      case UserRole.ADMIN:
      case UserRole.ADMIN_EDITOR:
        return 'default'
      case UserRole.EXPERT:
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const columns = [
    {
      key: 'email',
      header: 'User',
      render: (user: User) => (
        <div>
          <div className="font-medium text-foreground">{user.email}</div>
          <div className="text-sm text-muted-foreground">
            {user.first_name} {user.last_name}
          </div>
        </div>
      ),
      sortable: true
    },
    {
      key: 'role',
      header: 'Role',
      render: (user: User) => (
        <Badge variant={roleBadgeVariant(user.role)}>
          {user.role}
        </Badge>
      ),
      sortable: true
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (user: User) => (
        <Badge variant={user.is_active ? 'default' : 'error'}>
          {user.is_active ? 'Active' : 'Banned'}
        </Badge>
      ),
      sortable: true
    },
    {
      key: 'created_at',
      header: 'Joined',
      render: (user: User) => (
        <div className="text-sm text-muted-foreground">
          {new Date(user.created_at).toLocaleDateString()}
        </div>
      ),
      sortable: true
    },
    {
      key: 'last_login',
      header: 'Last Login',
      render: (user: User) => (
        <div className="text-sm text-muted-foreground">
          {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
        </div>
      ),
      sortable: true
    }
  ]

  if (loading && users.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading users...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 w-full">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <Users className="w-8 h-8 text-primary" />
            User Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage users, roles, and permissions across the platform
          </p>
        </div>
        <Button onClick={() => router.push('/admin/dashboard')}>
          <UserPlus className="w-4 h-4 mr-2" />
          Invite Admin
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Users</p>
              <p className="text-2xl font-bold text-foreground">{users.length}</p>
            </div>
            <Users className="w-8 h-8 text-primary opacity-50" />
          </div>
        </Card>
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Active</p>
              <p className="text-2xl font-bold text-success">
                {users.filter(u => u.is_active).length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-success opacity-50" />
          </div>
        </Card>
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Banned</p>
              <p className="text-2xl font-bold text-destructive">
                {users.filter(u => !u.is_active).length}
              </p>
            </div>
            <Ban className="w-8 h-8 text-destructive opacity-50" />
          </div>
        </Card>
        <Card className="glass border-border/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Experts</p>
              <p className="text-2xl font-bold text-accent">
                {users.filter(u => u.role === UserRole.EXPERT).length}
              </p>
            </div>
            <Shield className="w-8 h-8 text-accent opacity-50" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="glass border-border/50 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search by email or name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-background/50 border-border/50"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="px-4 py-2 rounded-lg border border-border bg-background text-foreground"
            >
              <option value="all">All Roles</option>
              <option value="client">Client</option>
              <option value="expert">Expert</option>
              <option value="admin">Admin</option>
              <option value="super_admin">Super Admin</option>
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 rounded-lg border border-border bg-background text-foreground"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="banned">Banned</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Users Table */}
      <DataTable
        data={filteredUsers}
        columns={columns}
        searchable={false}
        pagination={true}
        pageSize={10}
        actions={(user: User) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {user.role === UserRole.CLIENT && (
                <DropdownMenuItem onClick={() => {
                  setSelectedUser(user)
                  setPromoteDialogOpen(true)
                }}>
                  <UserCheck className="w-4 h-4 mr-2" />
                  Promote to Expert
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={() => handleRoleChange(user.user_id, 'expert')}>
                <Shield className="w-4 h-4 mr-2" />
                Change Role
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleBanUser(user.user_id, !user.is_active)}
                className={user.is_active ? 'text-destructive' : 'text-success'}
              >
                {user.is_active ? (
                  <>
                    <Ban className="w-4 h-4 mr-2" />
                    Ban User
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Unban User
                  </>
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      />

      {/* Promote Dialog */}
      <Dialog open={promoteDialogOpen} onOpenChange={setPromoteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Promote to Expert</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Are you sure you want to promote {selectedUser?.email} to expert?
            </p>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setPromoteDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => selectedUser && handlePromoteToExpert(selectedUser.user_id)}>
                Promote
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
