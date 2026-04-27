'use client'

import React, { useEffect, useState } from 'react'
import { Sidebar } from './Sidebar'
import { useTheme } from '@/contexts/ThemeContext'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { currentTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center" style={{ background: currentTheme.colors.bgPrimary }}>
        <div className="w-12 h-12 border-4 rounded-full animate-spin" 
          style={{ 
            borderColor: `${currentTheme.colors.accent}30`,
            borderTopColor: currentTheme.colors.accent
          }} 
        />
      </div>
    )
  }

  return (
    <div className="flex h-screen" style={{ background: currentTheme.colors.bgSecondary }}>
      <Sidebar />
      <main className="flex-1 overflow-hidden relative z-10" style={{ background: currentTheme.colors.bgPrimary }}>
        {children}
      </main>
    </div>
  )
}
