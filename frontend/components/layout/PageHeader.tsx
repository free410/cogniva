import React, { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

// 动态背景图标组件
function AnimatedIconBg({ children }: { children: React.ReactNode }) {
  const [animationOffset, setAnimationOffset] = useState(0)
  const frameRef = useRef<number>()
  
  useEffect(() => {
    let startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      setAnimationOffset(Math.sin(elapsed / 2000) * 0.5 + 0.5)
      frameRef.current = requestAnimationFrame(animate)
    }
    frameRef.current = requestAnimationFrame(animate)
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [])
  
  // 温暖的琥珀色渐变
  const colors = [
    '#FAF0DB', // 浅米色
    '#E8D5B5', // 深一点
    '#F5E6C8', // 暖黄
    '#EBD9B0', // 奶黄
  ]
  
  const color1 = colors[Math.floor(animationOffset * 2) % colors.length]
  const color2 = colors[(Math.floor(animationOffset * 2) + 1) % colors.length]
  const color3 = colors[(Math.floor(animationOffset * 2) + 2) % colors.length]
  
  return (
    <div
      style={{
        width: '2.75rem',
        height: '2.75rem',
        borderRadius: '0.75rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: `0 4px 15px rgba(194, 149, 74, ${0.3 + animationOffset * 0.2})`,
        backgroundImage: `linear-gradient(135deg, ${color1}, ${color2}, ${color3})`,
        backgroundSize: '300% 300%',
        animation: 'warm-flow 4s ease infinite',
      }}
    >
      {children}
    </div>
  )
}

interface PageHeaderProps {
  icon: React.ReactNode
  title: string
  subtitle: string
  actions?: React.ReactNode
  className?: string
}

export function PageHeader({ 
  icon, 
  title, 
  subtitle, 
  actions,
  className 
}: PageHeaderProps) {
  const { currentTheme } = useTheme()
  const { colors } = currentTheme

  return (
    <div 
      className={cn(
        "px-6 border-b flex items-center justify-between h-16 flex-shrink-0",
        className
      )}
      style={{ borderColor: colors.border }}
    >
      <div className="flex items-center gap-4">
        <AnimatedIconBg>
          {icon}
        </AnimatedIconBg>
        <div>
          <h1 className="text-lg font-bold" style={{ color: colors.textPrimary }}>{title}</h1>
          <p className="text-xs" style={{ color: colors.textMuted }}>{subtitle}</p>
        </div>
      </div>
      {actions && (
        <div className="flex items-center gap-3">
          {actions}
        </div>
      )}
    </div>
  )
}
