import React, { useCallback, useState } from 'react';
import { Upload, FileCode, X } from 'lucide-react';
import { useReviewStore } from '../../stores/reviewStore';
import { apiService } from '../../services/api';
import { webSocketService } from '../../services/websocket';

export const CodeUploader: React.FC = () => {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const { setCurrentTask } = useReviewStore();

  const handleFileSelect = useCallback(async (file: File) => {
    if (!file.name.match(/\.(py|js|ts|java|cpp|c|go|rs|rb)$/i)) {
      alert('请上传代码文件 (.py, .js, .ts, .java, .cpp, .c, .go, .rs, .rb)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      alert('文件大小不能超过10MB');
      return;
    }

    setUploading(true);
    try {
      const response = await apiService.uploadCodeFile(file);
      
      if (response.success && response.data) {
        const taskId = response.data.taskId;
        
        const newTask = {
          id: taskId,
          file,
          status: 'pending' as const,
          progress: 0,
          agents: [
            { name: 'Architect', status: 'idle', progress: 0, message: '等待中' },
            { name: 'Reviewer', status: 'idle', progress: 0, message: '等待中' },
            { name: 'Optimizer', status: 'idle', progress: 0, message: '等待中' },
            { name: 'User_Proxy', status: 'idle', progress: 0, message: '等待中' },
          ],
          createdAt: new Date(),
        };

        setCurrentTask(newTask);
        
        // 连接 WebSocket
        webSocketService.connect(taskId);
        
        // 启动审查
        await apiService.startCodeReview(taskId);
      }
    } catch (error) {
      console.error('上传失败:', error);
      alert('上传失败，请重试');
    } finally {
      setUploading(false);
    }
  }, [setCurrentTask]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
          ${dragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="code-upload"
          className="hidden"
          accept=".py,.js,.ts,.java,.cpp,.c,.go,.rs,.rb"
          onChange={handleFileInput}
          disabled={uploading}
        />
        
        <label htmlFor="code-upload" className="cursor-pointer block">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className={`p-3 rounded-full ${dragging ? 'bg-blue-100' : 'bg-gray-100'}`}>
              {uploading ? (
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
              ) : dragging ? (
                <Upload className="w-8 h-8 text-blue-500" />
              ) : (
                <FileCode className="w-8 h-8 text-gray-500" />
              )}
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {uploading ? '上传中...' : '上传代码文件'}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                拖放文件到此处，或点击选择文件
              </p>
            </div>
            
            <button
              type="button"
              className={`px-6 py-2 rounded-lg font-medium transition-colors
                ${uploading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
                }
              `}
              disabled={uploading}
              onClick={() => document.getElementById('code-upload')?.click()}
            >
              {uploading ? '上传中...' : '选择文件'}
            </button>
            
            <p className="text-xs text-gray-500 mt-4">
              支持格式: .py .js .ts .java .cpp .c .go .rs .rb
              <br />
              最大文件大小: 10MB
            </p>
          </div>
        </label>
      </div>
    </div>
  );
};