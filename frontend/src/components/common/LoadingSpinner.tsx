// src/components/common/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  color?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = '#0ea5e9' 
}) => {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-10 h-10',
    large: 'w-16 h-16'
  }
  
  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-solid border-current border-r-transparent`}
        style={{ color }}
        role="status"
      >
        <span className="sr-only">加载中...</span>
      </div>
    </div>
  )
}

export default LoadingSpinner