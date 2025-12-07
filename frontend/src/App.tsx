import React, { Suspense, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from '@components/layout/Layout'
import LoadingSpinner from '@components/common/LoadingSpinner'
import WebSocketProvider from '@services/WebSocketProvider'
import { useReviewStore } from '@stores/reviewStore'

// 页面组件 - 使用懒加载
const ReviewPage = React.lazy(() => import('@pages/review/ReviewPage'))
const HistoryPage = React.lazy(() => import('@pages/history/HistoryPage'))
const SettingsPage = React.lazy(() => import('@pages/settings/SettingsPage'))

// 全局加载状态
const GlobalLoader = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    background: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)'
  }}>
    <LoadingSpinner size="large" />
  </div>
)

// 页面切换动画
const PageTransition = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3 }}
  >
    {children}
  </motion.div>
)

function App() {
  const { initialize } = useReviewStore()

  // 应用初始化
  useEffect(() => {
    const initApp = async () => {
      try {
        // 初始化状态管理
        await initialize()
        
        // 检查服务连通性
        const checkHealth = async () => {
          try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/health`)
            if (!response.ok) throw new Error('后端服务不可用')
            console.log('✅ 后端服务连接正常')
          } catch (error) {
            console.warn('⚠️ 后端服务连接失败，部分功能可能受限')
          }
        }
        
        await checkHealth()
        
        // 注册 Service Worker (PWA)
        if ('serviceWorker' in navigator && import.meta.env.PROD) {
          navigator.serviceWorker.register('/sw.js')
            .then(registration => {
              console.log('✅ Service Worker 注册成功:', registration.scope)
            })
            .catch(error => {
              console.warn('⚠️ Service Worker 注册失败:', error)
            })
        }
        
        console.log('🎉 应用初始化完成')
      } catch (error) {
        console.error('应用初始化失败:', error)
      }
    }
    
    initApp()
    
    // 清理函数
    return () => {
      // 清理 WebSocket 连接等资源
    }
  }, [initialize])

  return (
    <WebSocketProvider>
      <BrowserRouter>
        <Suspense fallback={<GlobalLoader />}>
          <AnimatePresence mode="wait">
            <Routes>
              {/* 主布局 */}
              <Route path="/" element={<Layout />}>
                {/* 首页重定向 */}
                <Route index element={<Navigate to="/review" replace />} />
                
                {/* 代码审查页面 */}
                <Route 
                  path="review" 
                  element={
                    <PageTransition>
                      <ReviewPage />
                    </PageTransition>
                  } 
                />
                
                {/* 历史记录页面 */}
                <Route 
                  path="history" 
                  element={
                    <PageTransition>
                      <HistoryPage />
                    </PageTransition>
                  } 
                />
                
                {/* 设置页面 */}
                <Route 
                  path="settings" 
                  element={
                    <PageTransition>
                      <SettingsPage />
                    </PageTransition>
                  } 
                />
                
                {/* 404 页面 */}
                <Route 
                  path="*" 
                  element={
                    <div style={{ 
                      padding: '3rem', 
                      textAlign: 'center',
                      height: '60vh',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center'
                    }}>
                      <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>404</h1>
                      <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
                        找不到您访问的页面
                      </p>
                      <a 
                        href="/review" 
                        style={{
                          padding: '0.75rem 1.5rem',
                          background: '#0ea5e9',
                          color: 'white',
                          textDecoration: 'none',
                          borderRadius: '8px',
                          fontWeight: 500
                        }}
                      >
                        返回首页
                      </a>
                    </div>
                  } 
                />
              </Route>
            </Routes>
          </AnimatePresence>
        </Suspense>
      </BrowserRouter>
    </WebSocketProvider>
  )
}

export default App