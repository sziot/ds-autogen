import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    // 基础路径
    base: '/',
    
    // 插件配置
    plugins: [
      react({
        jsxImportSource: 'react',
        plugins: [
          ['@swc/plugin-emotion', {}]
        ]
      }),
      
      // 打包分析（仅生产环境启用）
      mode === 'production' && visualizer({
        filename: 'dist/stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true
      }),
    ].filter(Boolean),
    
    // 解析配置
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@stores': path.resolve(__dirname, './src/stores'),
        '@services': path.resolve(__dirname, './src/services'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@types': path.resolve(__dirname, './src/types'),
        '@assets': path.resolve(__dirname, './src/assets')
      }
    },
    
    // 开发服务器配置
    server: {
      port: 5173,
      host: true,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          ws: true
        },
        '/ws': {
          target: env.VITE_WS_URL?.replace('ws', 'http') || 'http://localhost:8000',
          changeOrigin: true,
          ws: true
        }
      },
      watch: {
        usePolling: false,
        interval: 100
      }
    },
    
    // 预览服务器配置
    preview: {
      port: 4173,
      host: true,
      open: true
    },
    
    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: mode === 'production' ? false : 'inline',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: true
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['@monaco-editor/react', 'lucide-react', 'framer-motion'],
            'state-vendor': ['zustand', '@tanstack/react-query'],
            'utils-vendor': ['axios', 'date-fns', 'clsx', 'socket.io-client']
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: ({ name }) => {
            if (/\.(gif|jpe?g|png|svg|webp)$/.test(name ?? '')) {
              return 'assets/images/[name]-[hash][extname]'
            }
            if (/\.css$/.test(name ?? '')) {
              return 'assets/css/[name]-[hash][extname]'
            }
            return 'assets/[name]-[hash][extname]'
          }
        }
      },
      chunkSizeWarningLimit: 1000
    },
    
    // 环境变量定义
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString())
    },
    
    // CSS 配置
    css: {
      devSourcemap: true,
      modules: {
        localsConvention: 'camelCase'
      }
    }
  }
})