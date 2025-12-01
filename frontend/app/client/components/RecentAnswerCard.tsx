'use client'

import { Star, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import { RecentAnswer } from '@/stores/useRealTimeStore'
import { cn } from '../lib/utils'

export function RecentAnswerCard({ answer }: { answer: RecentAnswer }) {
  const timeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / 60000)
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes} min${diffInMinutes > 1 ? 's' : ''} ago`
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`
  }

  return (
    <div
      className={cn(
        "animate-slide-up",
        "glass bg-gradient-to-br from-primary/10 via-purple-500/10 to-pink-500/10",
        "backdrop-blur-lg rounded-lg p-4 sm:p-5 border border-primary/20",
        "hover:border-primary/40 hover:shadow-lg transition-all duration-300",
        "group cursor-pointer"
      )}
    >
      <Link href={`/client/chat/${answer.id}`}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 bg-primary/20 text-primary text-xs font-medium rounded-full">
                {answer.subject}
              </span>
              <span className="text-xs text-muted-foreground">
                {timeAgo(answer.timestamp)}
              </span>
            </div>
            <p className="font-semibold text-foreground text-sm sm:text-base mb-2 line-clamp-2">
              {answer.question}
            </p>
            <p className="text-muted-foreground text-xs sm:text-sm line-clamp-2 mb-3">
              {answer.answer.slice(0, 120)}...
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">By {answer.expert}</span>
                {answer.rating && (
                  <div className="flex items-center gap-1">
                    <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    <span className="text-xs text-yellow-600 dark:text-yellow-400">{answer.rating}</span>
                  </div>
                )}
              </div>
              <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
          </div>
          {answer.image && (
            <div className="flex-shrink-0">
              <img 
                src={answer.image} 
                alt="Answer preview"
                className="w-16 h-16 sm:w-20 sm:h-20 rounded-lg object-cover border border-border/50"
              />
            </div>
          )}
        </div>
      </Link>
    </div>
  )
}

