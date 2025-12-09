import { useState } from 'react';
import CodeUpload from './components/CodeUpload';
import ReviewResults from './components/ReviewResults';
import { ReviewResult } from './types';

function App() {
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleReviewComplete = (result: ReviewResult) => {
    setReviewResult(result);
    setLoading(false);
  };

  const handleReviewStart = () => {
    setLoading(true);
    setReviewResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            AI代码审查系统
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            基于DeepSeek和AutoGen的智能代码审查平台
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Code Upload */}
          <div className="space-y-6">
            <CodeUpload
              onReviewStart={handleReviewStart}
              onReviewComplete={handleReviewComplete}
              loading={loading}
            />
          </div>

          {/* Right: Review Results */}
          <div className="space-y-6">
            <ReviewResults result={reviewResult} loading={loading} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

