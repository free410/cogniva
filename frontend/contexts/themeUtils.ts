import { ThemeConfig } from './ThemeContext'

// 主题颜色映射
export const accentColors: Record<string, { dark: string; light: string }> = {
  indigo: { dark: '#6366f1', light: '#6366f1' },
  purple: { dark: '#a855f7', light: '#a855f7' },
  sky: { dark: '#0ea5e9', light: '#0ea5e9' },
  emerald: { dark: '#10b981', light: '#10b981' },
  orange: { dark: '#f97316', light: '#f97316' },
  violet: { dark: '#8b5cf6', light: '#8b5cf6' },
  pink: { dark: '#ec4899', light: '#ec4899' },
}

// 获取强调色 RGBA
export function getAccentRgba(accent: string, opacity: number): string {
  const color = accentColors[accent] || accentColors.indigo
  return `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`
}

// 生成渐变背景类名
export function getAccentGradient(accent: string): string {
  const gradients: Record<string, string> = {
    indigo: 'from-indigo-500 to-purple-600',
    purple: 'from-purple-500 to-pink-600',
    sky: 'from-sky-500 to-blue-600',
    emerald: 'from-emerald-500 to-teal-600',
    orange: 'from-orange-500 to-amber-600',
    violet: 'from-violet-500 to-purple-600',
    pink: 'from-pink-500 to-rose-600',
  }
  return gradients[accent] || gradients.indigo
}

// 获取阴影类名
export function getAccentShadow(accent: string): string {
  const shadows: Record<string, string> = {
    indigo: 'shadow-indigo-500',
    purple: 'shadow-purple-500',
    sky: 'shadow-sky-500',
    emerald: 'shadow-emerald-500',
    orange: 'shadow-orange-500',
    violet: 'shadow-violet-500',
    pink: 'shadow-pink-500',
  }
  return shadows[accent] || shadows.indigo
}

// 获取文字颜色类名
export function getAccentText(accent: string, isDark: boolean): string {
  if (isDark) {
    const textColors: Record<string, string> = {
      indigo: 'text-indigo-400',
      purple: 'text-purple-400',
      sky: 'text-sky-400',
      emerald: 'text-emerald-400',
      orange: 'text-orange-400',
      violet: 'text-violet-400',
      pink: 'text-pink-400',
    }
    return textColors[accent] || textColors.indigo
  } else {
    const textColors: Record<string, string> = {
      indigo: 'text-indigo-600',
      purple: 'text-purple-600',
      sky: 'text-sky-600',
      emerald: 'text-emerald-600',
      orange: 'text-orange-600',
      violet: 'text-violet-600',
      pink: 'text-pink-600',
    }
    return textColors[accent] || textColors.indigo
  }
}

// 获取背景色类名
export function getAccentBg(accent: string, opacity: number = 0.1): string {
  const bgColors: Record<string, string> = {
    indigo: `bg-indigo-${Math.round(opacity * 100)}`,
    purple: `bg-purple-${Math.round(opacity * 100)}`,
    sky: `bg-sky-${Math.round(opacity * 100)}`,
    emerald: `bg-emerald-${Math.round(opacity * 100)}`,
    orange: `bg-orange-${Math.round(opacity * 100)}`,
    violet: `bg-violet-${Math.round(opacity * 100)}`,
    pink: `bg-pink-${Math.round(opacity * 100)}`,
  }
  return bgColors[accent] || bgColors.indigo
}

// 获取边框色类名
export function getAccentBorder(accent: string, opacity: number = 30): string {
  const borderColors: Record<string, string> = {
    indigo: `border-indigo-${opacity}`,
    purple: `border-purple-${opacity}`,
    sky: `border-sky-${opacity}`,
    emerald: `border-emerald-${opacity}`,
    orange: `border-orange-${opacity}`,
    violet: `border-violet-${opacity}`,
    pink: `border-pink-${opacity}`,
  }
  return borderColors[accent] || borderColors.indigo
}
