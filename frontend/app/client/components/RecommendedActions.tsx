'use client'

import { Gift, Users, TrendingUp, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { Button } from './ui/button'
import { cn } from '../lib/utils'

export function RecommendedActions({ credits = 12 }: { credits?: number }) {
  const actions = [
    {
      icon: Gift,
      title: 'Add Credits',
      description: credits < 20 ? 'Get 20% bonus on your next top-up!' : 'Top up your credits',
      cta: 'Add Credits',
      href: '/client/wallet',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Users,
      title: 'Invite Friends',
      description: 'Both you and your friend get 5 free questions!',
      cta: 'Invite Now',
      href: '/client/settings',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: TrendingUp,
      title: 'Upgrade Plan',
      description: 'Unlimited questions with premium features',
      cta: 'Upgrade',
      href: '/client/wallet',
      color: 'from-purple-500 to-pink-500'
    }
  ]

  return (
    <div className={cn(
      "glass bg-card/60 backdrop-blur-lg rounded-lg sm:rounded-lg p-4 sm:p-6",
      "border border-border/50 h-full flex flex-col"
    )}>
      <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-primary" />
        Recommended Actions
      </h3>
      <div className="space-y-4">
        {actions.map((action, index) => {
          const Icon = action.icon
          return (
            <Link key={index} href={action.href}>
              <div className={cn(
                "flex items-center gap-3 p-3 rounded-lg",
                "bg-gradient-to-r", action.color,
                "text-white hover:shadow-lg transition-all duration-300",
                "hover:scale-[1.02] active:scale-100"
              )}>
                <div className="p-1.5 bg-white/20 rounded-lg flex-shrink-0">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-xs sm:text-sm">{action.title}</p>
                  <p className="text-xs text-white/80 line-clamp-1">{action.description}</p>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  className="bg-white/20 hover:bg-white/30 text-white border-0 text-xs px-3 py-1.5 h-auto flex-shrink-0"
                >
                  {action.cta}
                </Button>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}


