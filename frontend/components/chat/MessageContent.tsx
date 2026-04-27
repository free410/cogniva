'use client'

import React, { useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

interface MessageContentProps {
  content: string
  className?: string
}

const MarkdownRenderer = ({ content, className, colors }: { content: string; className?: string; colors: any }) => {
  return (
    <ReactMarkdown
      className={cn("prose prose-sm max-w-none", className)}
      components={{
        h1: ({ children }) => <h2 className="text-lg font-bold mt-4 mb-2" style={{ color: colors.textPrimary }}>{children}</h2>,
        h2: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-2" style={{ color: colors.textPrimary }}>{children}</h3>,
        h3: ({ children }) => <h4 className="text-sm font-medium mt-2 mb-1" style={{ color: colors.textPrimary }}>{children}</h4>,
        p: ({ children }) => <p className="leading-relaxed my-2" style={{ color: colors.chatBubbleAiText }}>{children}</p>,
        ul: ({ children }) => <ul className="list-disc pl-5 my-2 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-5 my-2 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="leading-relaxed" style={{ color: colors.chatBubbleAiText }}>{children}</li>,
        strong: ({ children }) => <strong className="font-semibold" style={{ color: colors.textPrimary }}>{children}</strong>,
        code: ({ children }) => (
          <code 
            className="px-1.5 py-0.5 rounded text-sm font-mono border"
            style={{ 
              background: colors.isDark ? 'rgba(255,255,255,0.1)' : '#f3f4f6',
              borderColor: colors.isDark ? 'rgba(255,255,255,0.2)' : '#e5e7eb',
              color: colors.chatBubbleAiText
            }}
          >
            {children}
          </code>
        ),
        pre: ({ children }) => (
          <pre 
            className="rounded-lg p-3 overflow-x-auto my-2 border"
            style={{ 
              background: colors.isDark ? 'rgba(255,255,255,0.05)' : '#f9fafb',
              borderColor: colors.isDark ? 'rgba(255,255,255,0.1)' : '#e5e7eb'
            }}
          >
            {children}
          </pre>
        ),
        em: ({ children }) => <em className="italic" style={{ color: colors.chatBubbleAiText }}>{children}</em>,
        br: () => <br className="my-1" />,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export function MessageContent({ content, className }: MessageContentProps) {
  const { currentTheme } = useTheme()

  // Handle empty or undefined content
  if (!content || typeof content !== 'string') {
    return (
      <div className={cn("text-sm italic opacity-50", className)}>
        (empty response)
      </div>
    )
  }

  const cleanedContent = useMemo(() => {
    return content
      .replace(/^(\d+[\.、\.．])\s*(?=\d+[\.、\.．])/gm, '')
      .replace(/^[-*•]\s+/gm, '')
  }, [content])

  return (
    <div className={cn("space-y-2", className)}>
      <MarkdownRenderer content={cleanedContent} colors={currentTheme.colors} />
    </div>
  )
}
