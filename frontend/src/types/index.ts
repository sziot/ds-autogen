// 智能体相关类型
export interface AgentStatus {
  name: 'Architect' | 'Reviewer' | 'Optimizer' | 'User_Proxy';
  status: 'idle' | 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
  startTime?: Date;
  endTime?: Date;
}

export interface CodeReviewResult {
  id: string;
  fileName: string;
  originalContent: string;
  fixedContent: string;
  architectReport: string;
  reviewerReport: string;
  optimizerSummary: string;
  qualityScore: number;
  savedFilePath: string;
  createdAt: Date;
  diffStats: {
    additions: number;
    deletions: number;
    changes: number;
  };
}

export interface ReviewTask {
  id: string;
  file: File;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  agents: AgentStatus[];
  result?: CodeReviewResult;
  error?: string;
  createdAt: Date;
}

// WebSocket 消息类型
export type WebSocketMessage = 
  | AgentUpdateMessage
  | ProgressUpdateMessage
  | ResultMessage
  | ErrorMessage;

export interface AgentUpdateMessage {
  type: 'agent_update';
  data: {
    agent: string;
    status: AgentStatus['status'];
    message: string;
    progress: number;
  };
}

export interface ProgressUpdateMessage {
  type: 'progress_update';
  data: {
    taskId: string;
    overallProgress: number;
    currentStep: string;
  };
}

export interface ResultMessage {
  type: 'result';
  data: CodeReviewResult;
}

export interface ErrorMessage {
  type: 'error';
  data: {
    taskId: string;
    message: string;
    agent?: string;
  };
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadResponse {
  taskId: string;
  fileName: string;
  fileSize: number;
}

export interface DiffLine {
  type: 'added' | 'removed' | 'unchanged';
  content: string;
  lineNumber: number;
  oldLineNumber?: number;
  newLineNumber?: number;
}

export interface DiffChunk {
  oldStart: number;
  newStart: number;
  lines: DiffLine[];
}