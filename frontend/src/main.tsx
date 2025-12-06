import React from 'react'
import ReactDOM from 'react-dom/client'
import { HelmetProvider } from 'react-helmet-async'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './App.css'

// 创建 React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      retryDelay: 1000,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5分钟
      gcTime: 10 * 60 * 1000, // 10分钟
    },
    mutations: {
      retry: 1,
    },
  },
})

// 开发环境日志
if (import.meta.env.DEV) {
  console.log('🚀 启动 DeepSeek 代码审查前端...')
  console.log('📦 环境变量:', {
    MODE: import.meta.env.MODE,
    VITE_API_URL: import.meta.env.VITE_API_URL,
    VITE_WS_URL: import.meta.env.VITE_WS_URL,
    BASE_URL: import.meta.env.BASE_URL,
  })
}

// 错误边界处理
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React 错误:', error, errorInfo)
    // 这里可以上报错误到监控系统
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '2rem', 
          textAlign: 'center',
          fontFamily: 'system-ui, sans-serif'
        }}>
          <h2>😔 应用出现错误</h2>
          <p>请刷新页面或联系管理员</p>
          <button 
            onClick={() => window.location.reload()}
            style={{ 
              padding: '0.5rem 1rem',
              background: '#0ea5e9',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '1rem'
            }}
          >
            刷新页面
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// 渲染应用
try {
  const rootElement = document.getElementById('root')
  if (!rootElement) {
    throw new Error('找不到 #root 元素')
  }

  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <HelmetProvider>
          <QueryClientProvider client={queryClient}>
            <App />
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                  fontSize: '14px',
                },
                success: {
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#fff',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </QueryClientProvider>
        </HelmetProvider>
      </ErrorBoundary>
    </React.StrictMode>
  )
} catch (error) {
  console.error('应用启动失败:', error)
  document.body.innerHTML = `
    <div style="padding: 2rem; font-family: system-ui, sans-serif; text-align: center;">
      <h2>🚨 应用启动失败</h2>
      <p>${error instanceof Error ? error.message : '未知错误'}</p>
      <p>请检查浏览器控制台获取详细信息</p>
    </div>
  `
}