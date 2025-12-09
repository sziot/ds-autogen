import React, { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  Download,
  FileText,
  AlertCircle,
  FolderSearch,
} from 'lucide-react';
import ReactDiffViewer from 'react-diff-viewer-continued';
import { ReviewResult } from '../types';
import { downloadFixedFile } from '../services/api';

interface ReviewResultsProps {
  result: ReviewResult | null;
  loading: boolean;
}

export default function ReviewResults({ result, loading }: ReviewResultsProps) {
  const [activeTab, setActiveTab] = useState<'diff' | 'architect' | 'reviewer' | 'optimizer'>('diff');
  const [originalCode] = useState('');

  const handleDownload = async () => {
    if (!result?.file_name) return;

    try {
      const blob = await downloadFixedFile(result.file_name);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.file_name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('下载失败:', error);
      alert('下载失败，请重试');
    }
  };

  const baseCard = (children: React.ReactNode) => (
    <div className="bg-white rounded-2xl shadow-md border border-sky-100 overflow-hidden">
      <div className="bg-gradient-to-r from-cyan-500 to-sky-500 text-white px-5 py-3 flex items-center gap-2">
        <FolderSearch className="w-5 h-5" />
        <span className="text-lg font-semibold">3. 审查结果</span>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );

  if (loading) {
    return baseCard(
      <div className="flex items-center justify-center py-12">
        <div className="text-center space-y-2">
          <div className="inline-block animate-spin rounded-full h-9 w-9 border-b-2 border-sky-500"></div>
          <p className="text-slate-600">正在审查代码...</p>
        </div>
      </div>,
    );
  }

  if (!result) {
    return baseCard(
      <div className="flex items-center justify-center py-12">
        <div className="text-center text-slate-500 space-y-3">
          <FileText className="w-12 h-12 mx-auto opacity-60" />
          <p>等待代码审查结果</p>
        </div>
      </div>,
    );
  }

  if (!result.success) {
    return baseCard(
      <div className="flex items-start gap-3">
        <XCircle className="w-6 h-6 text-rose-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="text-lg font-semibold text-rose-900 mb-2">审查失败</h3>
          <p className="text-rose-700">{result.message || '未知错误'}</p>
        </div>
      </div>,
    );
  }

  return baseCard(
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" />
          <h2 className="text-lg font-semibold text-slate-900">审查完成</h2>
          {result.file_name && (
            <span className="inline-flex items-center rounded-full bg-slate-100 text-slate-700 text-xs px-3 py-1">
              {result.file_name}
            </span>
          )}
        </div>
        {result.fixed_code && (
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-sky-500 to-blue-500 hover:from-sky-600 hover:to-blue-600 text-white text-sm rounded-lg transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" />
            下载修复文件
          </button>
        )}
      </div>

      {/* Save Status */}
      {result.save_result && (
        <div
          className={`flex items-center gap-2 text-sm ${
            result.save_result.success ? 'text-emerald-600' : 'text-rose-600'
          }`}
        >
          {result.save_result.success ? (
            <CheckCircle className="w-4 h-4" />
          ) : (
            <AlertCircle className="w-4 h-4" />
          )}
          <span>{result.save_result.message}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200">
        {result.fixed_code && (
          <button
            onClick={() => setActiveTab('diff')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'diff'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            代码对比
          </button>
        )}
        {result.architect_report && (
          <button
            onClick={() => setActiveTab('architect')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'architect'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            架构分析
          </button>
        )}
        {result.reviewer_report && (
          <button
            onClick={() => setActiveTab('reviewer')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'reviewer'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            代码审查
          </button>
        )}
        {result.optimizer_report && (
          <button
            onClick={() => setActiveTab('optimizer')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'optimizer'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            优化报告
          </button>
        )}
      </div>

      {/* Content */}
      <div className="pt-2">
        {activeTab === 'diff' && result.fixed_code && (
          <div className="overflow-auto max-h-[600px] rounded-lg border border-slate-100">
            <ReactDiffViewer
              oldValue={originalCode || '原始代码'}
              newValue={result.fixed_code}
              splitView={true}
              leftTitle="原始代码"
              rightTitle="修复后代码"
              showDiffOnly={false}
              useDarkTheme={false}
            />
          </div>
        )}

        {activeTab === 'architect' && result.architect_report && (
          <div className="prose max-w-none">
            <pre className="bg-slate-50 border border-slate-100 p-4 rounded-lg overflow-auto text-sm text-slate-800">
              {result.architect_report}
            </pre>
          </div>
        )}

        {activeTab === 'reviewer' && result.reviewer_report && (
          <div className="prose max-w-none">
            <pre className="bg-slate-50 border border-slate-100 p-4 rounded-lg overflow-auto text-sm text-slate-800">
              {result.reviewer_report}
            </pre>
          </div>
        )}

        {activeTab === 'optimizer' && result.optimizer_report && (
          <div className="prose max-w-none">
            <pre className="bg-slate-50 border border-slate-100 p-4 rounded-lg overflow-auto text-sm text-slate-800">
              {result.optimizer_report}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

