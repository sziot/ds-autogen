import { WebSocketMessage, AgentUpdateMessage, ReviewTask } from '../types';
import { useReviewStore } from '../stores/reviewStore';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 3000;

  connect(taskId: string) {
    const url = `ws://localhost:8000/ws/review/${taskId}`;
    
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      useReviewStore.getState().setWsConnected(true);
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      useReviewStore.getState().setWsConnected(false);
      this.attemptReconnect(taskId);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(message: WebSocketMessage) {
    const store = useReviewStore.getState();

    switch (message.type) {
      case 'agent_update':
        this.handleAgentUpdate(message.data);
        break;
      
      case 'progress_update':
        store.updateTaskProgress(message.data.taskId, {
          progress: message.data.overallProgress,
        });
        break;
      
      case 'result':
        store.updateTaskProgress(message.data.id, {
          status: 'completed',
          progress: 100,
          result: message.data,
        });
        break;
      
      case 'error':
        store.updateTaskProgress(message.data.taskId, {
          status: 'failed',
          error: message.data.message,
        });
        break;
    }
  }

  private handleAgentUpdate(data: AgentUpdateMessage['data']) {
    const store = useReviewStore.getState();
    
    store.updateAgentStatus(data.agent, {
      status: data.status,
      message: data.message,
      progress: data.progress,
      ...(data.status === 'processing' && !store.currentTask?.startTime && { startTime: new Date() }),
      ...(data.status === 'completed' && { endTime: new Date() }),
    });
  }

  private attemptReconnect(taskId: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting attempt ${this.reconnectAttempts}...`);
      
      setTimeout(() => {
        this.connect(taskId);
      }, this.reconnectTimeout * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

export const webSocketService = new WebSocketService();