'use client'

import { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface StatCardProps {
  icon: LucideIcon
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  iconBgColor?: string
  iconColor?: string
  className?: string
}

export function StatCard({
  icon: Icon,
  title,
  value,
  change,
  trend,
  iconBgColor = "bg-primary/10",
  iconColor = "text-primary",
  className
}: StatCardProps) {
  return (
    <div className={cn(
      "card hover-lift group",
      className
    )}>
      <div className="flex items-center space-x-4">
        <div className={cn(
          "p-3 rounded-lg flex-shrink-0 transition-transform group-hover:scale-110",
          iconBgColor
        )}>
          <Icon className={cn("w-6 h-6", iconColor)} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm text-muted-foreground truncate">{title}</p>
          <div className="flex items-baseline gap-2 mt-1">
            <p className="text-2xl font-bold text-foreground truncate">{value}</p>
            {change && (
              <span className={cn(
                "text-xs font-medium",
                trend === 'up' && "text-success",
                trend === 'down' && "text-destructive",
                trend === 'neutral' && "text-muted-foreground"
              )}>
                {change}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

