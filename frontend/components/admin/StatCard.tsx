'use client'

import { Card } from '@/components/ui/card'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/app/client/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  subtitle?: string
  className?: string
  iconColor?: string
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  subtitle,
  className,
  iconColor = 'text-primary'
}: StatCardProps) {
  return (
    <Card className={cn(
      "glass border-border/50 p-6 hover:shadow-lg transition-all duration-300 group",
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-foreground">{value}</p>
            {trend && (
              <span className={cn(
                "text-sm font-medium",
                trend.isPositive ? "text-success" : "text-destructive"
              )}>
                {trend.isPositive ? '+' : '-'}{trend.value.toFixed(1)}%
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>
          )}
        </div>
        <div className={cn(
          "p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors",
          iconColor
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </Card>
  )
}

