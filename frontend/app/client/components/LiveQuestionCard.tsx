'use client'

import { Loader2, User } from 'lucide-react'
import { TypingDots } from './TypingDots'
import { LiveQuestion } from '@/stores/useRealTimeStore'
import { cn } from '../lib/utils'

export function LiveQuestionCard({ question }: { question: LiveQuestion }) {
  const getStatusText = () => {
    switch (question.status) {
      case 'typing':
        return (
          <>
            Expert is typing<TypingDots />
          </>
        )
      case 'processing':
        return 'AI is thinking…'
      case 'reviewing':
        return `${question.expert?.name || 'Expert'} is reviewing…`
      case 'delivered':
        return 'Delivered'
      default:
        return 'Processing…'
    }
  }

  return (
    <div
      className={cn(
        "glass bg-card/60 backdrop-blur-lg rounded-lg p-4 border border-border/50",
        "hover:bg-card/80 transition-all duration-300 animate-slide-in"
      )}
    >
      <div className="flex items-center gap-3">
        {question.expert ? (
          <div className="relative">
            {question.expert.avatar ? (
              <img 
                src={question.expert.avatar} 
                alt={question.expert.name}
                className="w-10 h-10 rounded-full border-2 border-primary/20" 
              />
            ) : (
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
            {question.status === 'typing' && (
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-background animate-pulse" />
            )}
          </div>
        ) : (
          <div className="w-10 h-10 bg-gradient-to-br from-primary/20 to-purple-500/20 rounded-full flex items-center justify-center">
            {question.status === 'processing' ? (
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
            ) : (
              <div className="w-5 h-5 bg-primary rounded-full" />
            )}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-foreground text-sm truncate">{question.subject}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {getStatusText()}
          </p>
        </div>
        <div className="text-xs text-muted-foreground">
          {new Date(question.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}

