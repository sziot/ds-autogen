import React, { useMemo } from 'react';
import { ChevronDown, ChevronUp, FileDiff, Download } from 'lucide-react';
import { CodeReviewResult, DiffChunk } from '../../types';
import { generateDiff } from '../../utils/diffUtils';
import { apiService } from '../../services/api';

interface DiffViewerProps {
  result: CodeReviewResult;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ result }) => {
  const [expandedChunks, setExpandedChunks] = React.useState<Set<number>>(new Set());

  const diffChunks = useMemo(() => {
    return generateDiff(result.originalContent, result.fixedContent);
  }, [result.originalContent, result.fixedContent]);

  const toggleChunk = (index: number) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedChunks(newExpanded);
  };

  const handleDownload = async () => {
    try {
      const blob = await apiService.downloadFixedFile(result.savedFilePath);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.fileName.replace(/(\.[^/.]+)$/, '_fixed$1');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('下载失败:', error);
      alert('下载失败，请重试');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* 头部 */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileDiff className="w-5 h-5 text-blue-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                代码差异对比
              </h3>
              <p className="text-sm text-gray-600">
                {result.fileName} • 质量评分: {result.qualityScore.toFixed(1)}/10
              </p>
            </div>
          </div>
          
          <button
            onClick={handleDownload}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-500 rounded-lg hover:bg-green-600 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            下载修复文件
          </button>
        </div>
        
        {/* 统计信息 */}
        <div className="flex items-center space-x-6 mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span className="text-sm text-gray-700">
              新增: {result.diffStats.additions} 行
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-sm text-gray-700">
              删除: {result.diffStats.deletions} 行
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-sm text-gray-700">
              总计: {result.diffStats.changes} 处更改
            </span>
          </div>
        </div>
      </div>

      {/* 差异内容 */}
      <div className="overflow-auto max-h-[600px]">
        {diffChunks.map((chunk, chunkIndex) => (
          <div key={chunkIndex} className="border-b border-gray-100">
            <div className="sticky top-0 z-10 bg-gray-50 px-4 py-2 border-b border-gray-200">
              <button
                onClick={() => toggleChunk(chunkIndex)}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-3">
                  {expandedChunks.has(chunkIndex) ? (
                    <ChevronUp className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  )}
                  <span className="text-sm font-medium text-gray-700">
                    @@ -{chunk.oldStart},{chunk.lines.filter(l => l.type !== 'added').length} 
                    +{chunk.newStart},{chunk.lines.filter(l => l.type !== 'removed').length} @@
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {chunk.lines.length} 行
                </span>
              </button>
            </div>

            {expandedChunks.has(chunkIndex) && (
              <div className="font-mono text-sm">
                {chunk.lines.map((line, lineIndex) => (
                  <div
                    key={`${chunkIndex}-${lineIndex}`}
                    className={`flex hover:bg-opacity-50 ${
                      line.type === 'added'
                        ? 'bg-green-50 hover:bg-green-100'
                        : line.type === 'removed'
                        ? 'bg-red-50 hover:bg-red-100'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex-shrink-0 w-16 px-2 py-1 text-xs text-gray-500 border-r border-gray-200 text-right">
                      {line.oldLineNumber || ' '}
                    </div>
                    <div className="flex-shrink-0 w-16 px-2 py-1 text-xs text-gray-500 border-r border-gray-200 text-right">
                      {line.newLineNumber || ' '}
                    </div>
                    <div className="flex-shrink-0 w-6 px-1 py-1 text-center border-r border-gray-200">
                      <span className={`inline-block w-2 h-2 rounded-full ${
                        line.type === 'added'
                          ? 'bg-green-500'
                          : line.type === 'removed'
                          ? 'bg-red-500'
                          : 'bg-transparent'
                      }`} />
                    </div>
                    <div className="flex-1 px-3 py-1 whitespace-pre">
                      {line.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};