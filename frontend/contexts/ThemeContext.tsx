'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type ThemeId = 'daylight' | 'cloud' | 'cream' | 'pearl' | 'midnight' | 'dusk' | 'slate' | 'carbon'

export interface ThemeColors {
  bgPrimary: string
  bgSecondary: string
  textPrimary: string
  textSecondary: string
  textMuted: string
  border: string
  accent: string
  accentText: string
  accentBg: string
  inputBg: string
  inputBorder: string
  cardBg: string
  cardBorder: string
  chatBubbleUser: string
  chatBubbleAi: string
  chatBubbleAiBorder: string
  chatBubbleAiText: string
  chatInputBg: string
  chatInputBorder: string
  chatInputText: string
  chatBarBg: string
  chatBarBorder: string
  isDark: boolean
}

export interface ThemeConfig {
  id: ThemeId
  name: string
  subname: string
  icon: string
  accentColor: string
  textPrimary: string
  textSecondary: string
  textMuted: string
  glassBorder: string
  colors: ThemeColors
}

export const themes: ThemeConfig[] = [
  { 
    id: 'daylight', 
    name: 'Daylight', 
    subname: '日光清新',
    icon: '☀',
    accentColor: '#0ea5e9',
    textPrimary: '#0f172a',
    textSecondary: '#475569',
    textMuted: '#94a3b8',
    glassBorder: 'rgba(255, 255, 255, 0.2)',
    colors: {
      bgPrimary: '#ffffff',
      bgSecondary: '#fafafa',
      textPrimary: '#0f172a',
      textSecondary: '#475569',
      textMuted: '#94a3b8',
      border: '#e5e7eb',
      accent: '#0ea5e9',
      accentText: '#0284c7',
      accentBg: '#f0f9ff',
      inputBg: '#ffffff',
      inputBorder: '#e5e7eb',
      cardBg: '#ffffff',
      cardBorder: '#f3f4f6',
      chatBubbleUser: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)',
      chatBubbleAi: '#ffffff',
      chatBubbleAiBorder: '#e5e7eb',
      chatBubbleAiText: '#334155',
      chatInputBg: '#ffffff',
      chatInputBorder: '#e5e7eb',
      chatInputText: '#0f172a',
      chatBarBg: 'rgba(255, 255, 255, 0.95)',
      chatBarBorder: '#e5e7eb',
      isDark: false,
    }
  },
  { 
    id: 'cloud', 
    name: 'Cloud', 
    subname: '云端灰蓝',
    icon: '☁',
    accentColor: '#64748b',
    textPrimary: '#1e293b',
    textSecondary: '#64748b',
    textMuted: '#94a3b8',
    glassBorder: 'rgba(255, 255, 255, 0.2)',
    colors: {
      bgPrimary: '#f1f5f9',
      bgSecondary: '#f5f5f7',
      textPrimary: '#1e293b',
      textSecondary: '#64748b',
      textMuted: '#94a3b8',
      border: '#d1d5db',
      accent: '#64748b',
      accentText: '#475569',
      accentBg: '#f8fafc',
      inputBg: '#ffffff',
      inputBorder: '#d1d5db',
      cardBg: '#ffffff',
      cardBorder: '#e5e7eb',
      chatBubbleUser: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
      chatBubbleAi: '#ffffff',
      chatBubbleAiBorder: '#e5e7eb',
      chatBubbleAiText: '#334155',
      chatInputBg: '#ffffff',
      chatInputBorder: '#d1d5db',
      chatInputText: '#1e293b',
      chatBarBg: 'rgba(241, 245, 249, 0.95)',
      chatBarBorder: '#d1d5db',
      isDark: false,
    }
  },
  { 
    id: 'cream', 
    name: 'Cream', 
    subname: '奶油暖调',
    icon: '◐',
    accentColor: '#c2954a',
    textPrimary: '#44403c',
    textSecondary: '#78716c',
    textMuted: '#a8a29e',
    glassBorder: 'rgba(254, 250, 232, 0.3)',
    colors: {
      bgPrimary: '#fefae8',
      bgSecondary: '#fcf9ef',
      textPrimary: '#44403c',
      textSecondary: '#78716c',
      textMuted: '#a8a29e',
      border: '#e8e2d6',
      accent: '#c2954a',
      accentText: '#92703a',
      accentBg: '#faf0db',
      inputBg: '#fffdf8',
      inputBorder: '#efe8d8',
      cardBg: '#fffdf8',
      cardBorder: '#f0e6d0',
      chatBubbleUser: 'linear-gradient(135deg, #c2954a 0%, #92703a 100%)',
      chatBubbleAi: '#faf0db',
      chatBubbleAiBorder: '#f0e6d0',
      chatBubbleAiText: '#57534e',
      chatInputBg: '#fffdf8',
      chatInputBorder: '#efe8d8',
      chatInputText: '#44403c',
      chatBarBg: 'rgba(254, 250, 239, 0.95)',
      chatBarBorder: '#e8e2d6',
      isDark: false,
    }
  },
  { 
    id: 'pearl', 
    name: 'Pearl', 
    subname: '珍珠白',
    icon: '◑',
    accentColor: '#7c3aed',
    textPrimary: '#4c1d95',
    textSecondary: '#7c3aed',
    textMuted: '#a78bfa',
    glassBorder: 'rgba(167, 139, 250, 0.3)',
    colors: {
      bgPrimary: '#fdfcff',
      bgSecondary: '#f5f3ff',
      textPrimary: '#4c1d95',
      textSecondary: '#7c3aed',
      textMuted: '#a78bfa',
      border: '#c4b5fd',
      accent: '#7c3aed',
      accentText: '#6d28d9',
      accentBg: '#ede9fe',
      inputBg: '#ffffff',
      inputBorder: '#c4b5fd',
      cardBg: '#ffffff',
      cardBorder: '#ddd6fe',
      chatBubbleUser: 'linear-gradient(135deg, #7c3aed 0%, #9333ea 100%)',
      chatBubbleAi: '#ffffff',
      chatBubbleAiBorder: '#ddd6fe',
      chatBubbleAiText: '#5b21b6',
      chatInputBg: '#ffffff',
      chatInputBorder: '#c4b5fd',
      chatInputText: '#4c1d95',
      chatBarBg: 'rgba(253, 252, 255, 0.95)',
      chatBarBorder: '#c4b5fd',
      isDark: false,
    }
  },
  { 
    id: 'midnight', 
    name: 'Midnight', 
    subname: '午夜蓝调',
    icon: '◓',
    accentColor: '#3b82f6',
    textPrimary: '#f1f5f9',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
    glassBorder: 'rgba(59, 130, 246, 0.2)',
    colors: {
      bgPrimary: '#0f1729',
      bgSecondary: '#1e293b',
      textPrimary: '#f1f5f9',
      textSecondary: '#94a3b8',
      textMuted: '#64748b',
      border: '#334155',
      accent: '#3b82f6',
      accentText: '#60a5fa',
      accentBg: 'rgba(59, 130, 246, 0.1)',
      inputBg: 'rgba(30, 41, 59, 0.8)',
      inputBorder: '#475569',
      cardBg: 'rgba(30, 41, 59, 0.6)',
      cardBorder: '#334155',
      chatBubbleUser: 'linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%)',
      chatBubbleAi: 'rgba(30, 41, 59, 0.8)',
      chatBubbleAiBorder: '#334155',
      chatBubbleAiText: '#e2e8f0',
      chatInputBg: 'rgba(30, 41, 59, 0.8)',
      chatInputBorder: '#475569',
      chatInputText: '#f1f5f9',
      chatBarBg: 'rgba(15, 23, 41, 0.8)',
      chatBarBorder: '#334155',
      isDark: true,
    }
  },
  { 
    id: 'dusk', 
    name: 'Dusk', 
    subname: '暮光紫',
    icon: '◕',
    accentColor: '#8b5cf6',
    textPrimary: '#ede9fe',
    textSecondary: '#c4b5fd',
    textMuted: '#a78bfa',
    glassBorder: 'rgba(139, 92, 246, 0.3)',
    colors: {
      bgPrimary: '#13111c',
      bgSecondary: '#1f1a2e',
      textPrimary: '#ede9fe',
      textSecondary: '#c4b5fd',
      textMuted: '#a78bfa',
      border: '#4c1d95',
      accent: '#8b5cf6',
      accentText: '#a78bfa',
      accentBg: 'rgba(139, 92, 246, 0.1)',
      inputBg: 'rgba(76, 29, 149, 0.3)',
      inputBorder: '#5b21b6',
      cardBg: 'rgba(76, 29, 149, 0.3)',
      cardBorder: '#4c1d95',
      chatBubbleUser: 'linear-gradient(135deg, #8b5cf6 0%, #9333ea 100%)',
      chatBubbleAi: 'rgba(76, 29, 149, 0.4)',
      chatBubbleAiBorder: '#5b21b6',
      chatBubbleAiText: '#e9d5ff',
      chatInputBg: 'rgba(76, 29, 149, 0.3)',
      chatInputBorder: '#5b21b6',
      chatInputText: '#ede9fe',
      chatBarBg: 'rgba(19, 17, 28, 0.8)',
      chatBarBorder: '#4c1d95',
      isDark: true,
    }
  },
  { 
    id: 'slate', 
    name: 'Slate', 
    subname: '石墨灰',
    icon: '◒',
    accentColor: '#71717a',
    textPrimary: '#fafafa',
    textSecondary: '#a1a1aa',
    textMuted: '#71717a',
    glassBorder: 'rgba(113, 113, 122, 0.3)',
    colors: {
      bgPrimary: '#18181b',
      bgSecondary: '#27272a',
      textPrimary: '#fafafa',
      textSecondary: '#a1a1aa',
      textMuted: '#71717a',
      border: '#3f3f46',
      accent: '#71717a',
      accentText: '#a1a1aa',
      accentBg: 'rgba(113, 113, 122, 0.1)',
      inputBg: 'rgba(39, 39, 42, 0.8)',
      inputBorder: '#52525b',
      cardBg: 'rgba(39, 39, 42, 0.6)',
      cardBorder: '#3f3f46',
      chatBubbleUser: 'linear-gradient(135deg, #71717a 0%, #57534e 100%)',
      chatBubbleAi: 'rgba(39, 39, 42, 0.7)',
      chatBubbleAiBorder: '#3f3f46',
      chatBubbleAiText: '#e4e4e7',
      chatInputBg: 'rgba(39, 39, 42, 0.8)',
      chatInputBorder: '#52525b',
      chatInputText: '#fafafa',
      chatBarBg: 'rgba(24, 24, 27, 0.8)',
      chatBarBorder: '#3f3f46',
      isDark: true,
    }
  },
  { 
    id: 'carbon', 
    name: 'Carbon', 
    subname: '碳素黑',
    icon: '◔',
    accentColor: '#a3a3a3',
    textPrimary: '#fafafa',
    textSecondary: '#a3a3a3',
    textMuted: '#737373',
    glassBorder: 'rgba(163, 163, 163, 0.3)',
    colors: {
      bgPrimary: '#0a0a0a',
      bgSecondary: '#171717',
      textPrimary: '#fafafa',
      textSecondary: '#a3a3a3',
      textMuted: '#737373',
      border: '#262626',
      accent: '#a3a3a3',
      accentText: '#a3a3a3',
      accentBg: 'rgba(163, 163, 163, 0.1)',
      inputBg: 'rgba(23, 23, 23, 0.8)',
      inputBorder: '#404040',
      cardBg: 'rgba(23, 23, 23, 0.7)',
      cardBorder: '#262626',
      chatBubbleUser: 'linear-gradient(135deg, #a3a3a3 0%, #737373 100%)',
      chatBubbleAi: 'rgba(23, 23, 23, 0.8)',
      chatBubbleAiBorder: '#262626',
      chatBubbleAiText: '#d4d4d4',
      chatInputBg: 'rgba(23, 23, 23, 0.8)',
      chatInputBorder: '#404040',
      chatInputText: '#fafafa',
      chatBarBg: 'rgba(10, 10, 10, 0.9)',
      chatBarBorder: '#262626',
      isDark: true,
    }
  },
]

interface ThemeContextType {
  currentTheme: ThemeConfig
  setCurrentTheme: (themeId: ThemeId) => void
  isDark: boolean
  colors: ThemeColors
}

const defaultTheme = themes[0]

const ThemeContext = createContext<ThemeContextType>({
  currentTheme: defaultTheme,
  setCurrentTheme: () => {},
  isDark: false,
  colors: defaultTheme.colors
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [currentTheme, setCurrentThemeState] = useState<ThemeConfig>(defaultTheme)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const savedThemeId = localStorage.getItem('app-theme') as ThemeId | null
    if (savedThemeId) {
      const theme = themes.find(t => t.id === savedThemeId)
      if (theme) {
        setCurrentThemeState(theme)
      }
    }
  }, [])

  const setCurrentTheme = (themeId: ThemeId) => {
    const theme = themes.find(t => t.id === themeId)
    if (theme) {
      setCurrentThemeState(theme)
      localStorage.setItem('app-theme', themeId)
    }
  }

  // 创建包含快捷属性的主题对象
  const themeWithShortcuts: ThemeConfig = {
    ...currentTheme,
    accentColor: currentTheme.colors.accent,
    textPrimary: currentTheme.colors.textPrimary,
    textSecondary: currentTheme.colors.textSecondary,
    textMuted: currentTheme.colors.textMuted,
    glassBorder: currentTheme.colors.border,
  }

  return (
    <ThemeContext.Provider value={{ 
      currentTheme: themeWithShortcuts, 
      setCurrentTheme,
      isDark: currentTheme.colors.isDark,
      colors: currentTheme.colors
    }}>
      {mounted ? children : (
        <div style={{ background: currentTheme.colors.bgPrimary, minHeight: '100vh' }} />
      )}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return useContext(ThemeContext)
}
