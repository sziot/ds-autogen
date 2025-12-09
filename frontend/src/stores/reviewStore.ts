import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { getReviewResult } from '../services/api';

export interface ReviewComment {
  line: number;
  comment: string;
  type: 'error' | 'warning' | 'info' | 'style';
}

interface ReviewState {
  taskId: string | null;
  originalCode: string;
  improvedCode: string;
  reviewResult: {
    comments: ReviewComment[];
  } | null;
  agentStatus: 'idle' | 'running' | 'completed' | 'error';
  error: string | null;
  setOriginalCode: (code: string) => void;
  setImprovedCode: (code: string) => void;
  startReview: (taskId: string) => void;
  pollReviewResult: (taskId: string) => Promise<void>;
  resetReview: () => void;
}

export const useReviewStore = create<ReviewState>()(
  persist(
    (set, get) => ({
      taskId: null,
      originalCode: '',
      improvedCode: '',
      reviewResult: null,
      agentStatus: 'idle',
      error: null,
      
      setOriginalCode: (code) => set({ originalCode: code }),
      setImprovedCode: (code) => set({ improvedCode: code }),
      
      startReview: (taskId) => set({ 
        taskId, 
        agentStatus: 'running',
        error: null
      }),
      
      pollReviewResult: async (taskId) => {
        try {
          const result = await getReviewResult(taskId);
          
          switch (result.status) {
            case 'completed':
              set({
                agentStatus: 'completed',
                originalCode: result.originalCode || '',
                improvedCode: result.improvedCode || '',
                reviewResult: {
                  comments: result.comments || []
                }
              });
              break;
              
            case 'failed':
              set({
                agentStatus: 'error',
                error: result.error || 'Review failed'
              });
              break;
              
            case 'pending':
            case 'processing':
              // Continue polling
              setTimeout(() => get().pollReviewResult(taskId), 1000);
              break;
          }
        } catch (error: any) {
          console.error('Error polling review result:', error);
          set({
            agentStatus: 'error',
            error: error.message || 'Failed to get review result'
          });
        }
      },
      
      resetReview: () => set({
        taskId: null,
        originalCode: '',
        improvedCode: '',
        reviewResult: null,
        agentStatus: 'idle',
        error: null
      })
    }),
    {
      name: 'review-storage',
    }
  )
);