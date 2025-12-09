import { useState, useRef } from 'react';
import { Upload, FileCode, Loader2, Eye, RotateCcw, FileText } from 'lucide-react';
import { reviewCode, reviewUploadedFile } from '../services/api';
import { ReviewResult } from '../types';

interface CodeUploadProps {
  onReviewStart: () => void;
  onReviewComplete: (result: ReviewResult) => void;
  onReset: () => void;
  onScrollToResult: () => void;
  loading: boolean;
}

export default function CodeUpload({
  onReviewStart,
  onReviewComplete,
  onReset,
  onScrollToResult,
  loading,
}: CodeUploadProps) {
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('example.py');
  const [showEditor, setShowEditor] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const content = await file.text();
      setCode(content);
      setFileName(file.name);
    } catch (error) {
      console.error('读取文件失败:', error);
      alert('读取文件失败，请重试');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleReview = async () => {
    if (!code.trim()) {
      alert('请先输入或上传代码');
      return;
    }

    onReviewStart();

    try {
      const result = await reviewCode(code, fileName);
      onReviewComplete(result);
    } catch (error: any) {
      console.error('代码审查失败:', error);
      alert(`代码审查失败: ${error.response?.data?.detail || error.message}`);
      onReviewComplete({
        success: false,
        message: error.response?.data?.detail || error.message,
      });
    }
  };

  const handleFileReview = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      alert('请先选择文件');
      return;
    }

    onReviewStart();

    try {
      const result = await reviewUploadedFile(file);
      onReviewComplete(result);
    } catch (error: any) {
      console.error('文件审查失败:', error);
      alert(`文件审查失败: ${error.response?.data?.detail || error.message}`);
      onReviewComplete({
        success: false,
        message: error.response?.data?.detail || error.message,
      });
    }
  };

  const handleReset = () => {
    setCode('');
    setFileName('example.py');
    setShowEditor(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onReset();
  };

  const handleViewResult = () => {
    onScrollToResult();
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-sky-100 overflow-hidden">
      <div className="bg-gradient-to-r from-sky-600 to-blue-600 text-white px-5 py-3 flex items-center gap-3">
        <span className="text-lg font-semibold">1. 上传代码文件</span>
      </div>

      <div className="p-6 space-y-4">
        {/* File Upload */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">
            选择代码文件
          </label>
          <div className="flex flex-col gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.go,.rs"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <div className="flex-1">
                <input
                  type="text"
                  value={fileName}
                  onChange={(e) => setFileName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-400 focus:border-transparent text-slate-700"
                  placeholder="upload_test.py"
                />
              </div>
              <button
                onClick={handleUploadClick}
                className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-sky-500 to-blue-500 text-white font-medium shadow-sm hover:from-sky-600 hover:to-blue-600 transition-colors"
                aria-label="上传文件"
              >
                <Upload className="w-4 h-4" />
                上传文件
              </button>
            </div>
          </div>
          <p className="text-sm text-slate-500">
            支持 Python、JavaScript、TypeScript、Java、C/C++ 等文件
          </p>
        </div>

        {/* Advanced editor toggle */}
        <div className="border border-slate-100 rounded-xl">
          <button
            type="button"
            onClick={() => setShowEditor((v) => !v)}
            className="w-full flex items-center justify-between px-4 py-3 text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <span className="inline-flex items-center gap-2">
              <FileText className="w-4 h-4 text-sky-500" />
              可选：直接粘贴代码
            </span>
            <span className="text-sm text-slate-500">
              {showEditor ? '收起' : '展开'}
            </span>
          </button>
          {showEditor && (
            <div className="p-4 pt-0">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                rows={12}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-400 focus:border-transparent font-mono text-sm text-slate-800"
                placeholder="在此粘贴或编写代码..."
              />
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <button
            onClick={handleReview}
            disabled={loading || (!code.trim() && !fileInputRef.current?.files?.[0])}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-sky-500 to-blue-500 text-white font-medium shadow-sm hover:from-sky-600 hover:to-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                审查中...
              </>
            ) : (
              <>
                <FileCode className="w-4 h-4" />
                审查代码
              </>
            )}
          </button>

          <button
            onClick={handleViewResult}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-cyan-500 text-white font-medium shadow-sm hover:bg-cyan-600 transition-colors"
          >
            <Eye className="w-4 h-4" />
            查看结果
          </button>

          <button
            onClick={handleFileReview}
            disabled={loading || !fileInputRef.current?.files?.[0]}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-emerald-500 text-white font-medium shadow-sm hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="w-4 h-4" />
            审查上传
          </button>

          <button
            onClick={handleReset}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-slate-500 text-white font-medium shadow-sm hover:bg-slate-600 transition-colors"
            type="button"
          >
            <RotateCcw className="w-4 h-4" />
            重置
          </button>
        </div>
      </div>
    </div>
  );
}
