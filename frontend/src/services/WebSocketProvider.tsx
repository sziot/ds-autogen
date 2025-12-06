// src/services/WebSocketProvider.tsx
import React, { createContext, useContext, ReactNode } from 'react'

interface WebSocketContextType {
  connect: (taskId: string) => void
  disconnect: () => void
  sendMessage: (message: any) => void
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const value = {
    connect: (taskId: string) => {
      console.log(`WebSocket 连接任务: ${taskId}`)
      // 实际实现中这里会建立 WebSocket 连接
    },
    disconnect: () => {
      console.log('WebSocket 断开连接')
    },
    sendMessage: (message: any) => {
      console.log('发送 WebSocket 消息:', message)
    }
  }
  
  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export default WebSocketProvider