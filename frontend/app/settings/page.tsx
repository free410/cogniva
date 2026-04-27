'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Layout } from '@/components'
import { Settings, Database, Cpu, Key, Save, Check, Loader2, Eye, EyeOff, Server, Sparkles, Shield, ChevronRight, Info, AlertCircle, RefreshCw } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'
import { API_BASE_URL } from '@/lib/api'

// 动态背景图标组件 - 温暖的琥珀色渐变（与其他页面统一）
function AnimatedIconBg({ children, emoji }: { children: React.ReactNode, emoji?: string }) {
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
      {emoji ? <span className="text-xl">{emoji}</span> : children}
    </div>
  )
}

const SETTINGS_SECTIONS = [
  { id: 'llm', label: '模型配置', icon: Cpu, desc: 'AI 大语言模型设置' },
  { id: 'providers', label: '服务商状态', icon: Sparkles, desc: '查看各服务商可用性' },
  { id: 'database', label: '数据存储', icon: Database, desc: '向量数据库配置' },
  { id: 'api', label: '安全密钥', icon: Shield, desc: 'API Keys 管理' },
]

interface ProviderStatus {
  name: string
  display_name: string
  available: boolean
  models: string[]
  error?: string
}

interface DatabaseStatus {
  connected: boolean
  host: string
  database: string
  vector_dimension: number
  status: string
}

interface SettingsData {
  default_provider: string
  ollama_url: string
  ollama_model: string
  openai_key: string
  anthropic_key: string
  dashscope_key: string
}

interface SettingInputProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
  hint?: string
  icon?: React.ReactNode
  disabled?: boolean
}

function SettingInput({ label, value, onChange, placeholder, type = 'text', hint, icon, disabled }: SettingInputProps) {
  const { currentTheme } = useTheme()
  const [showPassword, setShowPassword] = useState(false)
  const [focused, setFocused] = useState(false)
  const isPassword = type === 'password'
  const { colors } = currentTheme

  return (
    <div className="space-y-2">
      <label 
        className="block text-sm font-medium"
        style={{ color: colors.textSecondary }}
      >
        {label}
      </label>
      <div className="relative">
        {icon && (
          <div 
            className="absolute left-3 top-1/2 -translate-y-1/2 transition-colors duration-150 pointer-events-none"
            style={{ color: focused ? colors.accent : colors.textMuted }}
          >
            {icon}
          </div>
        )}
        <input
          type={isPassword && showPassword ? 'text' : type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={disabled}
          className="w-full px-10 py-3 rounded-lg transition-all duration-150 text-sm"
          style={{
            background: disabled ? colors.cardBg : colors.inputBg,
            border: `1px solid ${focused ? colors.accent : colors.inputBorder}`,
            color: disabled ? colors.textMuted : colors.chatInputText,
            outline: 'none',
            boxShadow: focused ? `0 0 0 3px ${colors.accent}20` : 'none',
            opacity: disabled ? 0.6 : 1
          }}
        />
        {isPassword && !disabled && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
            style={{ color: colors.textMuted }}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
      {hint && (
        <p className="text-xs" style={{ color: colors.textMuted }}>{hint}</p>
      )}
    </div>
  )
}

function SectionCard({ 
  name, 
  description, 
  badge,
  children 
}: { 
  name: string
  description: string
  badge?: { text: string; active: boolean; variant?: 'success' | 'warning' | 'info' }
  children: React.ReactNode 
}) {
  const { currentTheme } = useTheme()
  const { colors } = currentTheme

  const badgeColors = {
    success: { bg: colors.isDark ? 'rgba(34,197,94,0.2)' : '#dcfce7', text: '#22c55e' },
    warning: { bg: colors.isDark ? 'rgba(245,158,11,0.2)' : '#fffbeb', text: '#f59e0b' },
    info: { bg: colors.accentBg, text: colors.accent }
  }
  const badgeStyle = badge?.variant ? badgeColors[badge.variant] : badgeColors.info

  return (
    <div 
      className="rounded-xl overflow-hidden transition-all duration-200"
      style={{
        background: colors.cardBg,
        border: `1px solid ${colors.cardBorder}`
      }}
    >
      <div 
        className="px-5 py-4"
        style={{ borderBottom: `1px solid ${colors.border}` }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-sm" style={{ color: colors.textPrimary }}>{name}</h4>
            <p className="text-xs mt-0.5" style={{ color: colors.textMuted }}>{description}</p>
          </div>
          {badge?.active && (
            <span 
              className="px-2.5 py-1 rounded-full text-xs font-medium"
              style={{ background: badgeStyle.bg, color: badgeStyle.text }}
            >
              {badge.text}
            </span>
          )}
        </div>
      </div>
      <div className="p-5 space-y-4">
        {children}
      </div>
    </div>
  )
}

function StatusBadge({ children, variant = 'info' }: { children: React.ReactNode, variant?: 'success' | 'info' | 'warning' }) {
  const { currentTheme } = useTheme()
  const { colors } = currentTheme
  
  const styles = {
    success: { background: colors.isDark ? 'rgba(34,197,94,0.15)' : '#dcfce7', color: '#22c55e' },
    info: { background: colors.accentBg, color: colors.accent },
    warning: { background: colors.isDark ? 'rgba(245,158,11,0.15)' : '#fffbeb', color: '#f59e0b' },
  }
  
  return (
    <span 
      className="px-2.5 py-1 rounded-full text-xs font-medium"
      style={styles[variant]}
    >
      {children}
    </span>
  )
}

function ProviderCard({ provider }: { provider: ProviderStatus }) {
  const { currentTheme } = useTheme()
  const { colors } = currentTheme

  return (
    <div 
      className="p-4 rounded-lg transition-all"
      style={{ 
        background: colors.cardBg,
        border: `1px solid ${provider.available ? (colors.isDark ? 'rgba(34,197,94,0.3)' : '#bbf7d0') : colors.border}`
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ 
              background: provider.available 
                ? (colors.isDark ? 'rgba(34,197,94,0.2)' : '#dcfce7') 
                : colors.isDark ? 'rgba(239,68,68,0.2)' : '#fee2e2'
            }}
          >
            {provider.available ? (
              <Check className="w-5 h-5" style={{ color: '#22c55e' }} />
            ) : (
              <AlertCircle className="w-5 h-5" style={{ color: '#ef4444' }} />
            )}
          </div>
          <div>
            <p className="font-medium text-sm" style={{ color: colors.textPrimary }}>{provider.display_name}</p>
            <p className="text-xs mt-0.5" style={{ color: colors.textMuted }}>
              {provider.available ? '可用' : (provider.error || '不可用')}
            </p>
          </div>
        </div>
        <StatusBadge variant={provider.available ? 'success' : 'warning'}>
          {provider.available ? '在线' : '离线'}
        </StatusBadge>
      </div>
      {provider.models.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {provider.models.slice(0, 4).map((model, i) => (
            <span 
              key={i}
              className="px-2 py-0.5 rounded text-xs"
              style={{ 
                background: colors.isDark ? 'rgba(255,255,255,0.05)' : '#f1f5f9',
                color: colors.textMuted
              }}
            >
              {model}
            </span>
          ))}
          {provider.models.length > 4 && (
            <span className="text-xs" style={{ color: colors.textMuted }}>
              +{provider.models.length - 4} 更多
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default function SettingsPage() {
  const { currentTheme } = useTheme()
  const [activeSection, setActiveSection] = useState('llm')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [selectFocused, setSelectFocused] = useState(false)
  const [loading, setLoading] = useState(true)
  const [providers, setProviders] = useState<ProviderStatus[]>([])
  const [dbStatus, setDbStatus] = useState<DatabaseStatus | null>(null)
  const [settings, setSettings] = useState<SettingsData>({
    default_provider: 'deepseek',
    ollama_url: 'http://localhost:11434',
    ollama_model: 'llama3',
    openai_key: '',
    anthropic_key: '',
    dashscope_key: '',
  })
  const { colors } = currentTheme

  // 加载配置
  useEffect(() => {
    loadSettings()
    if (activeSection === 'providers') {
      loadProviderStatus()
    } else if (activeSection === 'database') {
      loadDatabaseStatus()
    }
  }, [activeSection])

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/`)
      if (response.ok) {
        const data = await response.json()
        setSettings(prev => ({
          ...prev,
          default_provider: data.default_provider || 'deepseek',
          ollama_url: data.ollama_url || 'http://localhost:11434',
          ollama_model: data.ollama_model || 'llama3',
        }))
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProviderStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/providers`)
      if (response.ok) {
        const data = await response.json()
        setProviders(data)
      }
    } catch (error) {
      console.error('加载服务商状态失败:', error)
    }
  }

  const loadDatabaseStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/database`)
      if (response.ok) {
        const data = await response.json()
        setDbStatus(data)
      }
    } catch (error) {
      console.error('加载数据库状态失败:', error)
      setDbStatus({
        connected: false,
        host: 'localhost:5432',
        database: 'knowledge_assistant',
        vector_dimension: 0,
        status: '连接失败'
      })
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          default_provider: settings.default_provider,
          ollama_url: settings.ollama_url,
          ollama_model: settings.ollama_model,
        })
      })
      
      if (response.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
      } else {
        console.error('保存失败')
      }
    } catch (error) {
      console.error('保存配置失败:', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <div className="h-full flex flex-col">
        {/* 页面标题 */}
        <div
          className="px-6 border-b flex-shrink-0 h-16 flex items-center relative overflow-hidden"
          style={{ borderColor: colors.border }}
        >
          {/* 装饰背景 */}
          <div
            className="absolute top-0 right-0 w-64 h-full pointer-events-none"
            style={{
              background: `linear-gradient(to left, ${currentTheme.colors.accent}08, transparent)`,
            }}
          />
          
          <div className="flex items-center gap-4 relative">
            <AnimatedIconBg>
              <Settings className="w-5 h-5 text-white" />
            </AnimatedIconBg>
            <div>
              <h1 className="text-lg font-bold" style={{ color: colors.textPrimary }}>设置中心</h1>
              <p className="text-xs" style={{ color: colors.textMuted }}>
                {currentTheme.icon} {currentTheme.name} · 自定义配置
              </p>
            </div>
          </div>
        </div>

        {/* 内容区 */}
        <div className="flex-1 flex overflow-hidden">
          {/* 左侧导航 */}
          <div 
            className="w-60 flex-shrink-0 p-4 overflow-y-auto"
            style={{ borderRight: `1px solid ${colors.border}` }}
          >
            <p 
              className="text-[10px] font-semibold uppercase tracking-wider mb-3 px-2"
              style={{ color: colors.textMuted }}
            >
              分类
            </p>
            <nav className="space-y-0.5">
            {SETTINGS_SECTIONS.map(section => {
              const Icon = section.icon
                const isActive = activeSection === section.id
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                    className="w-full text-left px-3 py-2.5 rounded-lg transition-all duration-150 flex items-center gap-3"
                    style={{
                      background: isActive ? colors.accentBg : 'transparent',
                      color: isActive ? colors.accentText : colors.textSecondary
                    }}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{section.label}</span>
                    {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
                </button>
              )
            })}
          </nav>

            {/* 帮助提示 */}
            <div 
              className="mt-6 p-3.5 rounded-lg"
              style={{ 
                background: colors.cardBg,
                border: `1px solid ${colors.border}`
              }}
            >
              <div className="flex items-start gap-2.5">
                <Info className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: colors.textMuted }} />
                <p className="text-xs" style={{ color: colors.textMuted }}>
                  配置更改后需要点击保存按钮才会生效
                </p>
              </div>
            </div>
        </div>

          {/* 右侧内容 */}
        <div className="flex-1 p-6 overflow-y-auto">
          {activeSection === 'llm' && (
              <div className="max-w-xl space-y-6">
                {/* 标题 */}
                <div>
                  <h2 className="text-base font-semibold flex items-center gap-2" style={{ color: colors.textPrimary }}>
                    <Cpu className="w-4 h-4" style={{ color: colors.accentText }} />
                    模型配置
                  </h2>
                  <p className="text-sm mt-1" style={{ color: colors.textMuted }}>
                    选择默认的 AI 模型提供商
                  </p>
                </div>

                {/* 提供商选择 */}
                <SectionCard
                  name="默认模型"
                  description="设置系统默认使用的 AI 模型提供商"
                  badge={{ text: '当前', active: true, variant: 'info' }}
                >
                  <select
                    value={settings.default_provider}
                    onChange={(e) => setSettings({ ...settings, default_provider: e.target.value })}
                    onFocus={() => setSelectFocused(true)}
                    onBlur={() => setSelectFocused(false)}
                    className="w-full px-3.5 py-2.5 rounded-lg transition-all duration-150 text-sm cursor-pointer"
                    style={{
                      background: colors.inputBg,
                      border: `1px solid ${selectFocused ? colors.accent : colors.inputBorder}`,
                      color: colors.chatInputText,
                      outline: 'none',
                      boxShadow: selectFocused ? `0 0 0 3px ${colors.accent}20` : 'none'
                    }}
                  >
                    <option value="deepseek">DeepSeek (推荐)</option>
                    <option value="openai">OpenAI (GPT-4, GPT-3.5)</option>
                    <option value="anthropic">Anthropic (Claude)</option>
                    <option value="ollama">Ollama (本地部署)</option>
                    <option value="dashscope">阿里云 (通义千问)</option>
                  </select>
                </SectionCard>

                {/* Ollama 配置 */}
                <SectionCard
                  name="Ollama 本地模型"
                  description="运行在本地的开源大语言模型"
                  badge={{ text: '可选', active: true, variant: 'info' }}
                >
                  <SettingInput
                    label="API 地址"
                    value={settings.ollama_url}
                    onChange={(v) => setSettings({ ...settings, ollama_url: v })}
                    placeholder="http://localhost:11434"
                    hint="确保 Ollama 服务已启动并正常运行"
                    icon={<Server className="w-4 h-4" />}
                  />
                  <SettingInput
                    label="模型名称"
                    value={settings.ollama_model}
                    onChange={(v) => setSettings({ ...settings, ollama_model: v })}
                    placeholder="llama3, mistral, codellama..."
                    hint='查看已安装模型: ollama list'
                    icon={<Sparkles className="w-4 h-4" />}
                  />
                </SectionCard>
              </div>
            )}

            {activeSection === 'providers' && (
              <div className="max-w-xl space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-base font-semibold flex items-center gap-2" style={{ color: colors.textPrimary }}>
                      <Sparkles className="w-4 h-4" style={{ color: colors.accentText }} />
                      服务商状态
                    </h2>
                    <p className="text-sm mt-1" style={{ color: colors.textMuted }}>
                      查看各 AI 服务商的可用性和配置状态
                    </p>
                  </div>
                  <button
                    onClick={loadProviderStatus}
                    className="p-2 rounded-lg transition-colors"
                    style={{ 
                      background: colors.cardBg,
                      color: colors.textMuted
                    }}
                    title="刷新状态"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-3">
                  {providers.map(provider => (
                    <ProviderCard key={provider.name} provider={provider} />
                  ))}
                  {providers.length === 0 && (
                    <div className="text-center py-8">
                      <Loader2 className="w-6 h-6 mx-auto animate-spin" style={{ color: colors.textMuted }} />
                      <p className="text-sm mt-2" style={{ color: colors.textMuted }}>加载中...</p>
                    </div>
                  )}
              </div>
            </div>
          )}

          {activeSection === 'database' && (
              <div className="max-w-xl space-y-6">
                {/* 标题 */}
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-base font-semibold flex items-center gap-2" style={{ color: colors.textPrimary }}>
                      <Database className="w-4 h-4" style={{ color: colors.accentText }} />
                      数据存储
                    </h2>
                    <p className="text-sm mt-1" style={{ color: colors.textMuted }}>
                      查看当前数据库配置状态
                    </p>
                  </div>
                  <button
                    onClick={loadDatabaseStatus}
                    className="p-2 rounded-lg transition-colors"
                    style={{ 
                      background: colors.cardBg,
                      color: colors.textMuted
                    }}
                    title="刷新状态"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>

                <SectionCard
                  name="PostgreSQL + pgvector"
                  description="向量数据库，用于存储和检索知识向量"
                >
                  {dbStatus ? (
                    <>
                      <div 
                        className="p-4 rounded-lg flex items-start gap-3"
                        style={{ 
                          background: dbStatus.connected 
                            ? (colors.isDark ? 'rgba(34,197,94,0.1)' : '#dcfce7')
                            : (colors.isDark ? 'rgba(239,68,68,0.1)' : '#fee2e2'),
                          border: `1px solid ${dbStatus.connected 
                            ? (colors.isDark ? 'rgba(34,197,94,0.3)' : '#bbf7d0')
                            : (colors.isDark ? 'rgba(239,68,68,0.3)' : '#fecaca')}`
                        }}
                      >
                        <div 
                          className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{ 
                            background: dbStatus.connected 
                              ? (colors.isDark ? 'rgba(34,197,94,0.2)' : '#dcfce7')
                              : (colors.isDark ? 'rgba(239,68,68,0.2)' : '#fecaca')
                          }}
                        >
                          {dbStatus.connected ? (
                            <Check className="w-4.5 h-4.5" style={{ color: '#22c55e' }} />
                          ) : (
                            <AlertCircle className="w-4.5 h-4.5" style={{ color: '#ef4444' }} />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-sm" style={{ color: colors.textPrimary }}>
                            {dbStatus.connected ? '数据库连接正常' : '数据库连接失败'}
                          </p>
                          <p className="text-xs mt-0.5" style={{ color: colors.textMuted }}>
                            {dbStatus.status}
                          </p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div 
                          className="p-3 rounded-lg"
                          style={{ background: colors.cardBg, border: `1px solid ${colors.border}` }}
                        >
                          <p className="text-xs" style={{ color: colors.textMuted }}>主机</p>
                          <p className="text-sm font-medium mt-0.5" style={{ color: colors.textPrimary }}>{dbStatus.host}</p>
                        </div>
                        <div 
                          className="p-3 rounded-lg"
                          style={{ background: colors.cardBg, border: `1px solid ${colors.border}` }}
                        >
                          <p className="text-xs" style={{ color: colors.textMuted }}>数据库</p>
                          <p className="text-sm font-medium mt-0.5" style={{ color: colors.textPrimary }}>{dbStatus.database}</p>
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        <StatusBadge variant={dbStatus.vector_dimension > 0 ? 'success' : 'warning'}>
                          向量维度: {dbStatus.vector_dimension || '未配置'}
                        </StatusBadge>
                        {dbStatus.connected && <StatusBadge variant="success">正常运行</StatusBadge>}
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-6">
                      <Loader2 className="w-6 h-6 mx-auto animate-spin" style={{ color: colors.textMuted }} />
                      <p className="text-sm mt-2" style={{ color: colors.textMuted }}>检查数据库连接中...</p>
                    </div>
                  )}
                </SectionCard>

                <div 
                  className="p-3.5 rounded-lg text-sm"
                  style={{ 
                    background: colors.cardBg,
                    border: `1px solid ${colors.border}`,
                    color: colors.textSecondary
                  }}
                >
                  <p>
                    数据库配置在 <code 
                    className="px-1.5 py-0.5 rounded text-xs font-mono font-medium"
                    style={{ background: colors.isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0' }}
                  >.env</code> 文件中管理
                </p>
              </div>
            </div>
          )}

          {activeSection === 'api' && (
              <div className="max-w-xl space-y-6">
                {/* 标题 */}
                <div>
                  <h2 className="text-base font-semibold flex items-center gap-2" style={{ color: colors.textPrimary }}>
                    <Shield className="w-4 h-4" style={{ color: colors.accentText }} />
                    API 密钥
                  </h2>
                  <p className="text-sm mt-1" style={{ color: colors.textMuted }}>
                    配置第三方 AI 服务的 API 密钥
                  </p>
                </div>

                {/* 安全提示 */}
                <div 
                  className="p-3.5 rounded-lg flex items-start gap-2.5"
                  style={{ 
                    background: colors.isDark ? 'rgba(245,158,11,0.1)' : '#fffbeb',
                    border: `1px solid ${colors.isDark ? 'rgba(245,158,11,0.3)' : '#fde68a'}`
                  }}
                >
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.isDark ? '#fbbf24' : '#d97706' }} />
                <div>
                    <p className="text-sm font-medium" style={{ color: colors.isDark ? '#fbbf24' : '#92400e' }}>
                      安全提示
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: colors.isDark ? 'rgba(251,191,36,0.7)' : '#a16207' }}>
                      API 密钥请在 <code className="font-mono">.env</code> 文件中配置，当前页面仅供查看
                    </p>
                  </div>
                </div>

                <SectionCard
                  name="DeepSeek"
                  description="DeepSeek Chat 和 DeepSeek Coder 模型"
                  badge={{ text: '推荐', active: true, variant: 'success' }}
                >
                  <div 
                    className="p-3 rounded-lg"
                    style={{ 
                      background: colors.isDark ? 'rgba(34,197,94,0.1)' : '#f0fdf4',
                      border: `1px solid ${colors.isDark ? 'rgba(34,197,94,0.2)' : '#bbf7d0'}`
                    }}
                  >
                    <p className="text-sm" style={{ color: colors.textSecondary }}>
                      请在 <code className="font-mono text-xs" style={{ color: colors.accent }}>.env</code> 文件中配置:
                    </p>
                    <p className="font-mono text-xs mt-2" style={{ color: colors.textMuted }}>
                      DEEPSEEK_API_KEY=your_api_key_here
                    </p>
                  </div>
                </SectionCard>

                <SectionCard
                  name="OpenAI"
                  description="GPT-4、GPT-3.5-Turbo 等模型"
                >
                  <div 
                    className="p-3 rounded-lg"
                    style={{ 
                      background: colors.cardBg,
                      border: `1px solid ${colors.border}`
                    }}
                  >
                    <p className="text-sm" style={{ color: colors.textSecondary }}>
                      请在 <code className="font-mono text-xs" style={{ color: colors.accent }}>.env</code> 文件中配置:
                    </p>
                    <p className="font-mono text-xs mt-2" style={{ color: colors.textMuted }}>
                      OPENAI_API_KEY=sk-your-api-key
                    </p>
                  </div>
                </SectionCard>

                <SectionCard
                  name="Anthropic"
                  description="Claude 3 系列模型"
                >
                  <div 
                    className="p-3 rounded-lg"
                    style={{ 
                      background: colors.cardBg,
                      border: `1px solid ${colors.border}`
                    }}
                  >
                    <p className="text-sm" style={{ color: colors.textSecondary }}>
                      请在 <code className="font-mono text-xs" style={{ color: colors.accent }}>.env</code> 文件中配置:
                    </p>
                    <p className="font-mono text-xs mt-2" style={{ color: colors.textMuted }}>
                      ANTHROPIC_API_KEY=sk-ant-your-api-key
                    </p>
                  </div>
                </SectionCard>

                <SectionCard
                  name="阿里云 DashScope"
                  description="通义千问、视觉模型等"
                >
                  <div 
                    className="p-3 rounded-lg"
                    style={{ 
                      background: colors.cardBg,
                      border: `1px solid ${colors.border}`
                    }}
                  >
                    <p className="text-sm" style={{ color: colors.textSecondary }}>
                      请在 <code className="font-mono text-xs" style={{ color: colors.accent }}>.env</code> 文件中配置:
                    </p>
                    <p className="font-mono text-xs mt-2" style={{ color: colors.textMuted }}>
                      DASHSCOPE_API_KEY=your-api-key
                    </p>
                </div>
                </SectionCard>
            </div>
          )}

            {/* 保存按钮 - 仅模型配置页面显示 */}
            {activeSection === 'llm' && (
              <div 
                className="mt-8 pt-5 flex items-center gap-3"
                style={{ borderTop: `1px solid ${colors.border}` }}
              >
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-150 shadow-sm"
                  style={{
                    background: saved ? '#22c55e' : colors.accent,
                    color: '#ffffff',
                    cursor: saving ? 'wait' : 'pointer',
                    opacity: saving ? 0.7 : 1
                  }}
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>保存中...</span>
                    </>
                  ) : saved ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>已保存</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>保存设置</span>
                    </>
                  )}
            </button>
                {saved && (
                  <span className="text-sm" style={{ color: '#22c55e' }}>
                    配置已更新
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
