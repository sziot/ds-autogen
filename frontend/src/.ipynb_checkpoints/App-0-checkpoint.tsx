// src/App.tsx - 绝对简化版
import React, { Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

const HomePage = () => (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 p-8">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        DeepSeek 代码审查系统
      </h1>
      <p className="text-gray-600 mb-8">
        前端应用已成功启动！请配置后端服务以使用完整功能。
      </p>
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">启动状态</h2>
        <div className="space-y-3">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span>前端服务运行正常</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
            <span>后端服务：{import.meta.env.VITE_API_URL || '未配置'}</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
            <span>运行模式：{import.meta.env.MODE}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
)

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="*" element={<HomePage />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App