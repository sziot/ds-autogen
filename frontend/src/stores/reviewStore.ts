import { create } from 'zustand';
import { ReviewTask, CodeReviewResult, AgentStatus } from '../types';

interface ReviewState {
  // 当前任务
  currentTask: ReviewTask | null;
  
  // 历史任务
  historyTasks: ReviewTask[];
  
  // 正在处理的任务
  processingTasks: ReviewTask[];
  
  // WebSocket 连接状态
  wsConnected: boolean;
  
  // Actions
  setCurrentTask: (task: ReviewTask | null) => void;
  addHistoryTask: (task: ReviewTask) => void;
  updateTaskProgress: (taskId: string, updates: Partial<ReviewTask>) => void;
  updateAgentStatus: (taskId: string, agentName: string, status: Partial<AgentStatus>) => void;
  setWsConnected: (connected: boolean) => void;
  
  // 工具函数
  getTaskById: (taskId: string) => ReviewTask | undefined;
  clearCompletedTasks: () => void;
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  currentTask: null,
  historyTasks: [],
  processingTasks: [],
  wsConnected: false,

  setCurrentTask: (task) => set({ currentTask: task }),

  addHistoryTask: (task) => 
    set((state) => ({ 
      historyTasks: [task, ...state.historyTasks] 
    })),

  updateTaskProgress: (taskId, updates) =>
    set((state) => ({
      processingTasks: state.processingTasks.map(task =>
        task.id === taskId ? { ...task, ...updates } : task
      ),
      historyTasks: state.historyTasks.map(task =>
        task.id === taskId ? { ...task, ...updates } : task
      ),
      currentTask: state.currentTask?.id === taskId 
        ? { ...state.currentTask, ...updates } 
        : state.currentTask,
    })),

  updateAgentStatus: (taskId, agentName, agentUpdates) =>
    set((state) => {
      const updateTaskAgents = (task: ReviewTask) => ({
        ...task,
        agents: task.agents.map(agent =>
          agent.name === agentName ? { ...agent, ...agentUpdates } : agent
        ),
      });

      return {
        processingTasks: state.processingTasks.map(task =>
          task.id === taskId ? updateTaskAgents(task) : task
        ),
        currentTask: state.currentTask?.id === taskId 
          ? updateTaskAgents(state.currentTask) 
          : state.currentTask,
      };
    }),

  setWsConnected: (connected) => set({ wsConnected: connected }),

  getTaskById: (taskId) => {
    const state = get();
    return (
      state.currentTask?.id === taskId ? state.currentTask :
      state.processingTasks.find(t => t.id === taskId) ||
      state.historyTasks.find(t => t.id === taskId)
    );
  },

  clearCompletedTasks: () =>
    set((state) => ({
      historyTasks: state.historyTasks.filter(task => 
        task.status !== 'completed' && task.status !== 'failed'
      ),
    })),
}));