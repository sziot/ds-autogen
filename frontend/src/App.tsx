import { useState } from 'react';
import CodeUpload from './components/CodeUpload';
import ReviewResults from './components/ReviewResults';
import { ReviewResult } from './types';

function App() {
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);

  const handleReviewComplete = (result: ReviewResult) => {
    setReviewResult(result);
    setLoading(false);
  };

  const handleReviewStart = () => {
    setLoading(true);
    setReviewResult(null);
    const id =
      typeof crypto !== 'undefined' && 'randomUUID' in crypto
        ? crypto.randomUUID()
        : `task-${Date.now()}`;
    setTaskId(id);
  };

  const handleReset = () => {
    setLoading(false);
    setReviewResult(null);
    setTaskId(null);
  };

  const scrollToResult = () => {
    const el = document.getElementById('result-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const statusLabel = loading
    ? '审查中...'
    : reviewResult?.success
    ? 'Optimizer 完成'
    : reviewResult
    ? '审查失败'
    : '等待上传';

  const progress = loading
    ? 65
    : reviewResult?.success
    ? 90
    : reviewResult
    ? 50
    : 15;

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
        {/* Hero */}
        <div className="text-center space-y-3">
          <div className="flex items-center justify-center">
            <div className="h-14 w-14 rounded-full bg-gradient-to-br from-pink-400 via-fuchsia-400 to-indigo-500 flex items-center justify-center shadow-md">
              <span className="text-2xl">🧠</span>
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900">
            DeepSeek 智能代码审查
          </h1>
          <p className="text-base sm:text-lg text-slate-600">
            上传您的代码，AI 自动分析、审查并优化
          </p>
        </div>

        {/* Upload Card */}
        <CodeUpload
          onReviewStart={handleReviewStart}
          onReviewComplete={handleReviewComplete}
          onReset={handleReset}
          onScrollToResult={scrollToResult}
          loading={loading}
        />

        {/* Status Card */}
        <section className="bg-white rounded-2xl shadow-md border border-sky-100 overflow-hidden">
          <div className="bg-gradient-to-r from-sky-600 to-cyan-500 text-white px-5 py-3 flex items-center gap-3">
            <span className="text-lg font-semibold">2. 审查状态</span>
          </div>

          <div className="p-5 space-y-3">
            <div className="flex flex-wrap items-center gap-3 text-sm sm:text-base">
              <span className="text-slate-700">状态：</span>
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
                  loading
                    ? 'bg-amber-100 text-amber-700'
                    : reviewResult?.success
                    ? 'bg-emerald-100 text-emerald-700'
                    : reviewResult
                    ? 'bg-rose-100 text-rose-700'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {statusLabel}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
              <span>任务ID:</span>
              <span className="font-mono text-indigo-600">
                {taskId || '--'}
              </span>
            </div>

            <div className="space-y-1">
              <div className="text-sm text-slate-600">总体进度</div>
              <div className="h-4 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-sky-400 via-cyan-500 to-blue-600 transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Results */}
        <section id="result-section">
          <ReviewResults result={reviewResult} loading={loading} />
        </section>
      </div>
    </div>
  );
}

export default App;

