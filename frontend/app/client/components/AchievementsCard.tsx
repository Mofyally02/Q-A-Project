'use client'

import { Flame, Award, Trophy, Star } from 'lucide-react'
import { cn } from '../lib/utils'

interface Achievement {
  type: 'streak' | 'badge' | 'level'
  label: string
  value: string | number
  icon: React.ComponentType<{ className?: string }>
  color: string
}

export function AchievementsCard({ 
  streak = 7, 
  totalQuestions = 47, 
  level = 'Gold',
  avgRating = 4.9 
}: {
  streak?: number
  totalQuestions?: number
  level?: string
  avgRating?: number
}) {
  const achievements: Achievement[] = [
    {
      type: 'streak',
      label: 'Day Streak',
      value: streak,
      icon: Flame,
      color: 'text-orange-500'
    },
    {
      type: 'badge',
      label: 'Questions',
      value: totalQuestions,
      icon: Award,
      color: 'text-blue-500'
    },
    {
      type: 'level',
      label: 'Level',
      value: level,
      icon: Trophy,
      color: 'text-yellow-500'
    },
    {
      type: 'badge',
      label: 'Avg Rating',
      value: avgRating,
      icon: Star,
      color: 'text-purple-500'
    }
  ]

  return (
    <div className={cn(
      "glass bg-card/60 backdrop-blur-lg rounded-lg sm:rounded-lg p-4 sm:p-6",
      "border border-border/50 h-full flex flex-col"
    )}>
      <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-yellow-500" />
        Achievements & Streaks
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        {achievements.map((achievement, index) => {
          const Icon = achievement.icon
          // Use a unique key based on label and index to avoid duplicates
          const uniqueKey = `achievement-${achievement.label.toLowerCase().replace(/\s+/g, '-')}-${index}`
          return (
            <div
              key={uniqueKey}
              className={cn(
                "flex flex-col items-center justify-center p-3 sm:p-4",
                "bg-background/50 rounded-lg border border-border/30",
                "hover:bg-background/70 transition-colors"
              )}
            >
              <Icon className={cn("w-6 h-6 sm:w-8 sm:h-8 mb-2", achievement.color)} />
              <p className="text-lg sm:text-2xl font-bold text-foreground">{achievement.value}</p>
              <p className="text-xs sm:text-sm text-muted-foreground text-center mt-1">
                {achievement.label}
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}


