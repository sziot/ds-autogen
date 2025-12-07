// src/components/layout/Layout.tsx
import React, { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { 
  Code2, History, Settings, Menu, X, 
  Upload, FileCode, Github, LogOut 
} from 'lucide-react'
import { motion } from 'framer-motion'

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  
  // 导航菜单项
  const navItems = [
    {
      path: '/review',
      label: '代码审查',
      icon: <Code2 className="w-5 h-5" />,
      description: '上传并分析代码'
    },
    {
      path: '/history',
      label: '历史记录',
      icon: <History className="w-5 h-5" />,
      description: '查看审查历史'
    },
    {
      path: '/settings',
      label: '设置',
      icon: <Settings className="w-5 h-5" />,
      description: '系统配置'
    }
  ]
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* 左侧：Logo和菜单按钮 */}
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 lg:hidden"
              >
                {sidebarOpen ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </button>
              
              <div className="flex items-center ml-4 lg:ml-0">
                <div className="flex items-center">
                  <Code2 className="w-8 h-8 text-primary-600" />
                  <div className="ml-3">
                    <h1 className="text-xl font-bold text-gray-900">
                      DeepSeek 代码审查
                    </h1>
                    <p className="text-xs text-gray-500">智能代码分析系统</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* 右侧：用户操作 */}
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full hover:bg-gray-100">
                <Github className="w-5 h-5 text-gray-500" />
              </button>
              <div className="hidden sm:block">
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">开发用户</p>
                    <p className="text-xs text-gray-500">admin@deepseek.com</p>
                  </div>
                  <button className="p-2 rounded-full hover:bg-gray-100">
                    <LogOut className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <div className="flex flex-1 overflow-hidden">
        {/* 侧边栏 - 桌面版 */}
        <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-white border-r border-gray-200">
          <nav className="flex-1 px-4 pb-4 space-y-2 mt-6">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-500'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <span className={`mr-3 ${isActive ? 'text-primary-600' : 'text-gray-400'}`}>
                    {item.icon}
                  </span>
                  {item.label}
                </Link>
              )
            })}
          </nav>
          
          {/* 侧边栏底部 */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">系统状态</p>
                <div className="flex items-center mt-1">
                  <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                  <span className="text-sm font-medium text-gray-900">运行正常</span>
                </div>
              </div>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                v1.0.0
              </span>
            </div>
          </div>
        </aside>
        
        {/* 侧边栏 - 移动版 */}
        {sidebarOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="lg:hidden fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200"
          >
            <div className="px-4 pb-4 space-y-2 mt-16">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className="flex items-center px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50 hover:text-gray-900"
                >
                  <span className="mr-3 text-gray-400">{item.icon}</span>
                  {item.label}
                  <span className="ml-auto text-xs text-gray-500">
                    {item.description}
                  </span>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
        
        {/* 主内容区域 */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
      
      {/* 移动端遮罩层 */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 z-30 bg-gray-600 bg-opacity-50"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default Layout