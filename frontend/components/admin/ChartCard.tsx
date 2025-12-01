'use client'

import { Card } from '@/components/ui/card'
import { cn } from '@/app/client/lib/utils'

interface ChartCardProps {
  title: string
  subtitle?: string
  children: React.ReactNode
  className?: string
  actions?: React.ReactNode
}

export function ChartCard({
  title,
  subtitle,
  children,
  className,
  actions
}: ChartCardProps) {
  return (
    <Card className={cn(
      "glass border-border/50 p-6",
      className
    )}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          {subtitle && (
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        {actions && <div>{actions}</div>}
      </div>
      <div className="h-[300px]">
        {children}
      </div>
    </Card>
  )
}

