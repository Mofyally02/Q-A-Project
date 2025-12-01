'use client'

export function TypingDots() {
  return (
    <span className="inline-flex items-center ml-1">
      <span className="animate-bounce [animation-delay:-0.3s]">.</span>
      <span className="animate-bounce [animation-delay:-0.15s]">.</span>
      <span className="animate-bounce">.</span>
    </span>
  )
}


