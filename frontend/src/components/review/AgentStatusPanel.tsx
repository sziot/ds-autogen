import React from 'react';
import { 
  Building, 
  Search, 
  Zap, 
  User, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  PlayCircle 
} from 'lucide-react';
import { AgentStatus } from '../../types';
import { useReviewStore } from '../../stores/reviewStore';

const AgentIcons = {
  Architect: Building,
  Reviewer: Search,
  Optimizer: Zap,
  User_Proxy: User,
};

const StatusIcons = {
  idle: Clock,
  processing: PlayCircle,
  completed: CheckCircle,
  error: AlertCircle,
};

const StatusColors = {
  idle: 'bg-gray-100 text-gray-600',
  processing: 'bg-blue-100 text-blue-600',
  completed: 'bg-green-100 text-green-600',
  error: 'bg-red-100 text-red-600',
};

export const AgentStatusPanel: React.FC = () => {
  const { currentTask } = useReviewStore();

  if (!currentTask) return null;

  const overallProgress = currentTask.progress;
  const allCompleted = currentTask.agents.every(agent => agent.status === 'completed');

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          智能体协作状态
        </h3>
        
        {/* 总体进度条 */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">总体进度</span>
            <span className="text-sm font-semibold text-blue-600">
              {overallProgress}%
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 transition-all duration-500 ease-out"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* 智能体状态网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {currentTask.agents.map((agent) => {
          const AgentIcon = AgentIcons[agent.name as keyof typeof AgentIcons];
          const StatusIcon = StatusIcons[agent.status];
          const statusColor = StatusColors[agent.status];

          return (
            <div
              key={agent.name}
              className={`border rounded-lg p-4 transition-all duration-300 hover:shadow-md ${
                agent.status === 'completed' 
                  ? 'border-green-200' 
                  : agent.status === 'processing'
                  ? 'border-blue-200'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${statusColor}`}>
                    <AgentIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{agent.name}</h4>
                    <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium mt-1 ${statusColor}`}>
                      <StatusIcon className="w-3 h-3 mr-1" />
                      {agent.status === 'idle' && '等待中'}
                      {agent.status === 'processing' && '处理中'}
                      {agent.status === 'completed' && '已完成'}
                      {agent.status === 'error' && '错误'}
                    </div>
                  </div>
                </div>
              </div>

              {/* 进度条 */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>进度</span>
                  <span>{agent.progress}%</span>
                </div>
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-400 transition-all duration-500"
                    style={{ width: `${agent.progress}%` }}
                  />
                </div>
              </div>

              {/* 消息 */}
              <div className="text-sm text-gray-600">
                <p className="truncate">{agent.message}</p>
                {agent.startTime && (
                  <p className="text-xs text-gray-400 mt-1">
                    开始: {agent.startTime.toLocaleTimeString()}
                  </