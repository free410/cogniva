'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { Sparkles, Lock, User, Eye, EyeOff, ArrowRight, Loader2 } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AuthPage() {
  const router = useRouter()
  const { currentTheme } = useTheme()
  const { isAuthenticated, isLoading: authLoading, isReady } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [bgOffset, setBgOffset] = useState(0)
  const frameRef = useRef<number>()

  const { colors } = currentTheme

  // 已登录用户直接跳转到聊天页面
  useEffect(() => {
    if (isReady && !authLoading && isAuthenticated) {
      router.replace('/chat')
    }
  }, [isReady, authLoading, isAuthenticated, router])

  // 背景动画
  useEffect(() => {
    let startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      setBgOffset(Math.sin(elapsed / 3000) * 0.5 + 0.5)
      frameRef.current = requestAnimationFrame(animate)
    }
    frameRef.current = requestAnimationFrame(animate)
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [])

  // 温暖的琥珀色系
  const warmColors = [
    '#F5E6C8', '#E8D5B5', '#DBC9A8', '#FAF0DB'
  ]

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.username.trim()) {
      newErrors.username = '请输入用户名'
    } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(formData.username)) {
      newErrors.username = '用户名需3-20个字符，只能包含字母、数字和下划线'
    }
    
    if (!formData.password) {
      newErrors.password = '请输入密码'
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少需要6个字符'
    }
    
    if (!isLogin && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!validateForm()) return

    setIsSubmitting(true)

    const timeoutId = setTimeout(() => {
      setIsSubmitting(false)
      setError('请求超时，请检查后端服务是否正常运行')
    }, 30000)

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
      const body = { username: formData.username, password: formData.password }

      console.log(`正在${isLogin ? '登录' : '注册'}...`, `${API_BASE}${endpoint}`)

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(25000)
      })

      clearTimeout(timeoutId)

      const data = await response.json()
      console.log('响应:', response.status, data)

      if (!response.ok) {
        throw new Error(data.detail || `请求失败 (${response.status})`)
      }

      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      console.log('登录/注册成功，跳转到聊天页面')
      // 使用 window.location 强制页面刷新，确保状态正确加载
      window.location.href = '/chat'
    } catch (err: any) {
      clearTimeout(timeoutId)
      console.error('请求错误:', err)

      if (err.name === 'TimeoutError' || err.name === 'AbortError') {
        setError('请求超时，请检查后端服务是否正常运行')
      } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        setError('无法连接到服务器，请确保后端服务已启动')
      } else {
        setError(err.message || '网络错误，请重试')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  // 加载中或已登录时不显示登录表单
  if (!isReady || authLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: '#fefcf8' }}
      >
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: '#c2954a' }} />
      </div>
    )
  }

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{ background: '#fefcf8' }}
    >
      {/* 渐变流动背景层 */}
      <div 
        className="absolute inset-0"
        style={{
          backgroundImage: `linear-gradient(
            ${-30 + bgOffset * 60}deg,
            #fff8f0 0%,
            #fef0e8 25%,
            #fff5eb 50%,
            #fef8f2 75%,
            #fff8f0 100%
          )`,
          backgroundSize: '400% 400%',
          animation: 'gradientFlow 10s ease infinite',
        }}
      />
      
      {/* 主光晕 - 中心 */}
      <div 
        className="absolute w-[800px] h-[800px] rounded-full"
        style={{
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'radial-gradient(circle, rgba(255, 230, 210, 0.8) 0%, rgba(255, 245, 235, 0.4) 40%, transparent 70%)',
          animation: 'glowPulse 4s ease-in-out infinite',
        }}
      />
      
      {/* 左上角光晕 */}
      <div 
        className="absolute w-[500px] h-[500px] rounded-full"
        style={{
          top: '-150px',
          left: '-150px',
          background: 'radial-gradient(circle, rgba(255, 215, 180, 0.6) 0%, rgba(255, 235, 215, 0.3) 50%, transparent 70%)',
          animation: 'float1 8s ease-in-out infinite',
        }}
      />
      
      {/* 右下角光晕 */}
      <div 
        className="absolute w-[600px] h-[600px] rounded-full"
        style={{
          bottom: '-200px',
          right: '-200px',
          background: 'radial-gradient(circle, rgba(255, 220, 190, 0.5) 0%, rgba(255, 240, 225, 0.2) 50%, transparent 70%)',
          animation: 'float2 10s ease-in-out infinite',
        }}
      />
      
      {/* 漂浮的光斑装饰 */}
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className="absolute rounded-full"
          style={{
            width: `${12 + (i % 3) * 8}px`,
            height: `${12 + (i % 3) * 8}px`,
            left: `${10 + i * 11}%`,
            top: `${15 + (i % 4) * 20}%`,
            background: `radial-gradient(circle, rgba(255, 180, 120, ${0.3 + (i % 3) * 0.15}) 0%, rgba(255, 200, 150, 0.1) 70%, transparent 100%)`,
            animation: `sparkle ${2 + i * 0.4}s ease-in-out infinite`,
            animationDelay: `${i * 0.3}s`,
          }}
        />
      ))}
      
      {/* 渐变线条装饰 */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ opacity: 0.3 }}>
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ffd4a8" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#ffe4cc" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#ffd4a8" stopOpacity="0.8" />
          </linearGradient>
        </defs>
        <line 
          x1={`${-20 + bgOffset * 40}%`} y1="0" 
          x2={`${80 + bgOffset * 40}%`} y2="100%" 
          stroke="url(#lineGrad)" 
          strokeWidth="1"
          style={{ animation: 'lineMove 8s linear infinite' }}
        />
        <line 
          x1={`${120 - bgOffset * 40}%`} y1="0" 
          x2={`${20 - bgOffset * 40}%`} y2="100%" 
          stroke="url(#lineGrad)" 
          strokeWidth="1"
          style={{ animation: 'lineMove 8s linear infinite reverse' }}
        />
      </svg>
      
      {/* 动态圆环 */}
      <div 
        className="absolute border-2 rounded-full"
        style={{
          width: '400px',
          height: '400px',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          borderColor: 'rgba(255, 200, 160, 0.3)',
          animation: 'ringRotate 20s linear infinite',
        }}
      />
      <div 
        className="absolute border border-dashed rounded-full"
        style={{
          width: '600px',
          height: '600px',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          borderColor: 'rgba(255, 180, 130, 0.2)',
          animation: 'ringRotate 30s linear infinite reverse',
        }}
      />

      <style jsx>{`
        @keyframes gradientFlow {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes glowPulse {
          0%, 100% { opacity: 0.6; transform: translate(-50%, -50%) scale(1); }
          50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
        }
        @keyframes float1 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(40px, 30px); }
          66% { transform: translate(-20px, 50px); }
        }
        @keyframes float2 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(-50px, -40px); }
          66% { transform: translate(30px, -20px); }
        }
        @keyframes sparkle {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.5); }
        }
        @keyframes ringRotate {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        @keyframes lineMove {
          0% { transform: translateX(-100px); }
          100% { transform: translateX(100px); }
        }
      `}</style>

      {/* 主卡片 */}
      <div 
        className="relative w-full max-w-md rounded-3xl shadow-2xl overflow-hidden backdrop-blur-sm"
        style={{ 
          background: 'rgba(255, 255, 255, 0.85)',
          border: '1px solid rgba(255, 255, 255, 0.5)'
        }}
      >
        {/* 顶部装饰条 */}
        <div 
          className="h-1.5 w-full"
          style={{ background: `linear-gradient(90deg, #c2954a, #e8d5b5)` }}
        />

        <div className="p-8">
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div 
              className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg mb-4"
              style={{ 
                background: `linear-gradient(135deg, #c2954a, #e8d5b5)`,
                boxShadow: `0 8px 30px rgba(194, 149, 74, 0.4)`
              }}
            >
              <Sparkles className="w-8 h-8" style={{ color: '#ffffff' }} />
            </div>
            <h1 className="text-2xl font-bold" style={{ color: '#5c4a2a' }}>
              Cogniva
            </h1>
            <p className="text-sm mt-1" style={{ color: '#8b7355' }}>
              {isLogin ? '欢迎回来' : '创建您的账户'}
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div 
              className="mb-4 p-3 rounded-lg text-sm"
              style={{ 
                background: '#fef2f2', 
                border: '1px solid #fecaca',
                color: '#dc2626'
              }}
            >
              {error}
            </div>
          )}

          {/* 表单 */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* 用户名 */}
            <div>
              <label 
                className="block text-sm font-medium mb-2"
                style={{ color: '#5c4a2a' }}
              >
                用户名
              </label>
              <div className="relative">
                <div 
                  className="absolute left-4 top-1/2 -translate-y-1/2"
                  style={{ color: '#8b7355' }}
                >
                  <User className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="请输入用户名"
                  className="w-full pl-12 pr-4 py-3 rounded-xl transition-all duration-200 text-sm"
                  style={{
                    background: '#faf0db',
                    border: `1px solid ${errors.username ? '#ef4444' : '#e8d5b5'}`,
                    color: '#5c4a2a'
                  }}
                />
              </div>
              {errors.username && (
                <p className="text-red-500 text-xs mt-1">{errors.username}</p>
              )}
            </div>

            {/* 密码 */}
            <div>
              <label 
                className="block text-sm font-medium mb-2"
                style={{ color: '#5c4a2a' }}
              >
                密码
              </label>
              <div className="relative">
                <div 
                  className="absolute left-4 top-1/2 -translate-y-1/2"
                  style={{ color: '#8b7355' }}
                >
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="请输入密码"
                  className="w-full pl-12 pr-12 py-3 rounded-xl transition-all duration-200 text-sm"
                  style={{
                    background: '#faf0db',
                    border: `1px solid ${errors.password ? '#ef4444' : '#e8d5b5'}`,
                    color: '#5c4a2a'
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 transition-colors"
                  style={{ color: '#8b7355' }}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">{errors.password}</p>
              )}
            </div>

            {/* 确认密码 */}
            {!isLogin && (
              <div className="animate-fade-in">
                <label 
                  className="block text-sm font-medium mb-2"
                  style={{ color: '#5c4a2a' }}
                >
                  确认密码
                </label>
                <div className="relative">
                  <div 
                    className="absolute left-4 top-1/2 -translate-y-1/2"
                    style={{ color: '#8b7355' }}
                  >
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="请再次输入密码"
                    className="w-full pl-12 pr-4 py-3 rounded-xl transition-all duration-200 text-sm"
                    style={{
                      background: '#faf0db',
                      border: `1px solid ${errors.confirmPassword ? '#ef4444' : '#e8d5b5'}`,
                      color: '#5c4a2a'
                    }}
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            {/* 记住我 / 忘记密码 */}
            {isLogin && (
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="w-4 h-4 rounded accent-amber-600"
                  />
                  <span style={{ color: '#8b7355' }}>记住我</span>
                </label>
                <button
                  type="button"
                  className="font-medium transition-colors hover:underline"
                  style={{ color: '#c2954a' }}
                >
                  忘记密码？
                </button>
              </div>
            )}

            {/* 提交按钮 */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-70"
              style={{
                background: `linear-gradient(135deg, #c2954a, #e8d5b5)`,
                color: '#ffffff'
              }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>{isLogin ? '登录中...' : '注册中...'}</span>
                </>
              ) : (
                <>
                  <span>{isLogin ? '登 录' : '注 册'}</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* 分隔线 */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px" style={{ background: '#e8d5b5' }} />
            <span className="text-xs" style={{ color: '#8b7355' }}>或</span>
            <div className="flex-1 h-px" style={{ background: '#e8d5b5' }} />
          </div>

          {/* 社交登录 */}
          <button
            type="button"
            className="w-full py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-3 transition-all duration-200"
            style={{
              background: '#faf0db',
              border: '1px solid #e8d5b5',
              color: '#5c4a2a'
            }}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            使用 Google 登录
          </button>

          {/* 切换登录/注册 */}
          <p className="text-center text-sm mt-6" style={{ color: '#8b7355' }}>
            {isLogin ? '还没有账户？' : '已有账户？'}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setErrors({})
                setError('')
                setFormData({ username: '', password: '', confirmPassword: '' })
              }}
              className="font-semibold ml-1 transition-colors hover:underline"
              style={{ color: '#c2954a' }}
            >
              {isLogin ? '立即注册' : '去登录'}
            </button>
          </p>
        </div>

        {/* 底部装饰 */}
        <div 
          className="px-8 py-4 text-center text-xs"
          style={{ 
            background: '#faf0db',
            borderTop: '1px solid #e8d5b5'
          }}
        >
          <p style={{ color: '#8b7355' }}>
            登录即表示您同意我们的
            <button className="underline hover:no-underline mx-1" style={{ color: '#c2954a' }}>
              服务条款
            </button>
            和
            <button className="underline hover:no-underline mx-1" style={{ color: '#c2954a' }}>
              隐私政策
            </button>
          </p>
        </div>
      </div>

      {/* 版权信息 */}
      <p className="absolute bottom-4 text-xs" style={{ color: '#8b7355' }}>
        © 2024 Cogniva. All rights reserved.
      </p>
    </div>
  )
}
