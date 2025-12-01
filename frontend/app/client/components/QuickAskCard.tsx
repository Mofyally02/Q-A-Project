'use client'

import { useState } from 'react'
import { Plus, Upload, X, Send } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Button } from './ui/button'
import { cn } from '../lib/utils'
import toast from 'react-hot-toast'

export function QuickAskCard() {
  const router = useRouter()
  const [question, setQuestion] = useState('')
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onloadend = () => setImagePreview(reader.result as string)
        reader.readAsDataURL(file)
      } else {
        toast.error('Please upload an image file')
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) {
      toast.error('Please enter a question')
      return
    }

    setIsSubmitting(true)
    // Navigate to ask page with pre-filled question
    router.push(`/client/ask?q=${encodeURIComponent(question)}`)
  }

  return (
    <div className={cn(
      "glass bg-card/60 backdrop-blur-lg rounded-lg sm:rounded-lg p-4 sm:p-6",
      "border border-border/50 shadow-lg",
      "h-full flex flex-col"
    )}>
      <form onSubmit={handleSubmit} className="space-y-4 flex-1 flex flex-col">
        <div className="flex items-center gap-2 mb-3">
          <Plus className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">Quick Ask</h3>
        </div>
        
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What is the derivative of x²?"
          rows={3}
          className={cn(
            "w-full px-4 py-3 rounded-lg border border-border",
            "bg-background/50 focus:bg-background",
            "focus:ring-2 focus:ring-primary focus:border-primary",
            "resize-none text-sm sm:text-base",
            "placeholder:text-muted-foreground"
          )}
        />

        {imagePreview && (
          <div className="relative">
            <img 
              src={imagePreview} 
              alt="Preview" 
              className="w-full h-32 object-cover rounded-lg"
            />
            <button
              type="button"
              onClick={() => setImagePreview(null)}
              className="absolute top-2 right-2 p-1 bg-destructive text-destructive-foreground rounded-full hover:bg-destructive/90"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="flex items-center gap-2">
          <label className="flex-1">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => {
                const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement | null
                fileInput?.click()
              }}
            >
              <Upload className="w-4 h-4 mr-2" />
              {imagePreview ? 'Change Image' : 'Add Image'}
            </Button>
          </label>
          <Button
            type="submit"
            size="sm"
            disabled={isSubmitting || !question.trim()}
            className="flex-shrink-0"
          >
            <Send className="w-4 h-4 mr-2" />
            Send
          </Button>
        </div>
      </form>
    </div>
  )
}


