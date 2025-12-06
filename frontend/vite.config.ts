import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { visualizer } from 'rollup-plugin-visualizer';
import compression from 'vite-plugin-compression';
import { VitePWA } from 'vite-plugin-pwa';
import svgr from 'vite-plugin-svgr';
import path from 'path';
import type { UserConfig } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isProduction = mode === 'production';
  const isAnalyze = process.env.ANALYZE === 'true';

  const config: UserConfig = {
    base: '/',
    
    plugins: [
      react({
        jsxImportSource: 'react',
        plugins: [
          ['@swc/plugin-emotion', {}]
        ]
      }),
      
      svgr({
        svgrOptions: {
          icon: true,
          memo: true,
        },
      }),

      // PWA 配置（仅生产环境）
      env.VITE_ENABLE_PWA === 'true' && VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
        manifest: {
          name: 'DeepSeek 代码审查系统',
          short_name: 'CodeReview',
          description: '基于AI的智能代码审查系统',
          theme_color: '#0ea5e9',
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          scope: '/',
          start_url: '/',
          icons: [
            {
              src: '/pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: '/pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            },
            {
              src: '/pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            }
          ]
        }
      }),

      // 压缩配置（仅生产环境）
      isProduction && compression({
        algorithm: 'gzip',
        ext: '.gz',
        threshold: 10240,
        deleteOriginFile: false
      }),

      isProduction && compression({
        algorithm: 'brotliCompress',
        ext: '.br',
        threshold: 10240,
        deleteOriginFile: false
      }),

      // 打包分析（需要时启用）
      isAnalyze && visualizer({
        filename: './dist/stats.html',
        open: true,
        gzipSize: true,
        brotliSize: true
      }),
    ].filter(Boolean),

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
        '@theme': path.resolve(__dirname, './src/theme')
      }
    },

    server: {
      port: 5173,
      host: true,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/ws': {
          target: env.VITE_WS_URL?.replace('ws', 'http') || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true
        }
      },
      watch: {
        usePolling: true,
        interval: 1000
      }
    },

    preview: {
      port: 4173,
      host: true,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },

    build: {
      outDir: 'dist',
      sourcemap: isProduction ? 'hidden' : true,
      minify: isProduction ? 'terser' : false,
      cssMinify: isProduction,
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info']
        },
        mangle: {
          safari10: true
        }
      } : undefined,
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['lucide-react', 'framer-motion'],
            'editor-vendor': ['monaco-editor', '@monaco-editor/react'],
            'state-vendor': ['zustand', '@tanstack/react-query'],
            'utils-vendor': ['axios', 'date-fns', 'clsx']
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: ({ name }) => {
            if (/\.(gif|jpe?g|png|svg)$/.test(name ?? '')) {
              return 'assets/images/[name]-[hash][extname]';
            }
            if (/\.css$/.test(name ?? '')) {
              return 'assets/css/[name]-[hash][extname]';
            }
            return 'assets/[name]-[hash][extname]';
          }
        }
      },
      chunkSizeWarningLimit: 1000,
      reportCompressedSize: false
    },

    esbuild: {
      drop: isProduction ? ['console', 'debugger'] : []
    },

    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'monaco-editor/esm/vs/editor/editor.api',
        'monaco-editor/esm/vs/language/typescript/ts.worker',
        'monaco-editor/esm/vs/language/json/json.worker',
        'monaco-editor/esm/vs/language/css/css.worker',
        'monaco-editor/esm/vs/language/html/html.worker',
        'monaco-editor/esm/vs/basic-languages/python/python'
      ],
      exclude: ['@swc/core']
    },

    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'src/test/',
          '**/*.d.ts',
          '**/*.config.*',
          '**/index.ts'
        ]
      }
    }
  };

  return config;
});