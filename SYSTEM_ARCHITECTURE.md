# 系统架构树形图

## 完整项目结构

```
ds-autogen/
│
├── backend/                                    # 后端服务目录
│   ├── __init__.py                            # Python包初始化
│   ├── main.py                                # FastAPI主服务入口
│   │   ├── FastAPI应用初始化
│   │   ├── CORS中间件配置
│   │   ├── 路由定义
│   │   │   ├── POST /api/review              # 代码审查接口
│   │   │   ├── POST /api/review/upload       # 文件上传审查
│   │   │   ├── GET  /api/download/{filename} # 下载修复文件
│   │   │   ├── GET  /api/files               # 列出修复文件
│   │   │   └── WS   /ws/review               # WebSocket实时审查
│   │   └── 启动配置
│   │
│   ├── autogen_reviewer.py                    # 代码审查核心实现 ⭐
│   │   ├── CodeReviewSystem类
│   │   │   ├── __init__()                    # 初始化智能体系统
│   │   │   ├── _create_user_proxy()          # 创建User_Proxy
│   │   │   ├── _create_architect()           # 创建Architect智能体
│   │   │   ├── _create_reviewer()            # 创建Reviewer智能体
│   │   │   ├── _create_optimizer()           # 创建Optimizer智能体
│   │   │   ├── review_code()                 # 主审查流程
│   │   │   └── _extract_results_from_chat()  # 提取结果
│   │   └── create_review_system()            # 工厂函数
│   │
│   ├── agents.py                              # 智能体定义（旧版，可参考）
│   │   └── CodeReviewAgents类
│   │
│   ├── tools.py                               # 工具函数模块 ⭐
│   │   ├── save_fixed_code()                 # 保存修复代码工具
│   │   ├── register_tools_to_user_proxy()    # 注册工具函数
│   │   └── TOOL_DESCRIPTIONS                 # 工具描述字典
│   │
│   ├── example_optimizer_tool_call.py         # Optimizer工具调用示例 ⭐
│   │   ├── 方式1: 通过消息明确指示
│   │   ├── 方式2: 使用函数调用机制
│   │   ├── 方式3: 通过GroupChat实现
│   │   └── 方式4: 完整消息格式示例
│   │
│   ├── requirements.txt                       # Python依赖列表
│   │   ├── fastapi==0.115.4
│   │   ├── uvicorn[standard]==0.32.0
│   │   ├── autogen==0.10.2
│   │   ├── openai==2.9.0
│   │   └── 其他依赖...
│   │
│   └── .env.example                           # 环境变量示例
│       ├── DEEPSEEK_API_KEY
│       └── DEEPSEEK_BASE_URL
│
├── frontend/                                  # 前端应用目录
│   ├── index.html                            # HTML入口文件
│   │
│   ├── package.json                          # 前端依赖配置
│   │   ├── dependencies
│   │   │   ├── react ^18.3.1
│   │   │   ├── react-dom ^18.3.1
│   │   │   ├── react-diff-viewer-continued
│   │   │   ├── axios
│   │   │   └── lucide-react
│   │   └── devDependencies
│   │       ├── vite ^5.4.2
│   │       ├── typescript ^5.5.4
│   │       ├── tailwindcss ^3.4.13
│   │       └── 其他开发依赖...
│   │
│   ├── vite.config.ts                        # Vite构建配置
│   │   ├── React插件配置
│   │   ├── 路径别名(@)
│   │   └── 代理配置(/api, /ws)
│   │
│   ├── tsconfig.json                         # TypeScript配置
│   ├── tsconfig.node.json                   # Node环境TS配置
│   ├── tailwind.config.js                   # Tailwind CSS配置
│   ├── postcss.config.js                    # PostCSS配置
│   │
│   └── src/                                  # 源代码目录
│       ├── main.tsx                          # 应用入口
│       │   └── ReactDOM渲染
│       │
│       ├── App.tsx                           # 主应用组件
│       │   ├── 状态管理(reviewResult, loading)
│       │   ├── CodeUpload组件
│       │   └── ReviewResults组件
│       │
│       ├── index.css                         # 全局样式
│       │   └── Tailwind指令和基础样式
│       │
│       ├── vite-env.d.ts                     # Vite类型定义
│       │
│       ├── types/                            # TypeScript类型定义
│       │   └── index.ts
│       │       ├── ReviewResult接口
│       │       └── CodeFile接口
│       │
│       ├── services/                         # API服务层
│       │   └── api.ts
│       │       ├── reviewCode()              # 代码审查API
│       │       ├── reviewUploadedFile()      # 文件上传审查
│       │       ├── downloadFixedFile()       # 下载修复文件
│       │       └── listFixedFiles()         # 列出修复文件
│       │
│       └── components/                       # React组件
│           ├── CodeUpload.tsx                # 代码上传组件
│           │   ├── 文件选择功能
│           │   ├── 代码编辑器(textarea)
│           │   ├── 文件名输入
│           │   └── 审查按钮
│           │
│           └── ReviewResults.tsx             # 审查结果展示组件 ⭐
│               ├── 加载状态显示
│               ├── 错误状态显示
│               ├── 成功状态显示
│               ├── Tab切换(代码对比/架构分析/审查报告/优化报告)
│               ├── ReactDiffViewer组件      # 代码差异对比
│               └── 文件下载功能
│
├── fixed/                                    # 修复后代码保存目录(运行时生成)
│   └── [修复后的文件].py
│
├── README.md                                 # 项目说明文档
├── ARCHITECTURE.md                           # 架构详细说明
└── SYSTEM_ARCHITECTURE.md                    # 本文件(系统架构树形图)
```

## 智能体协作流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    代码审查智能体协作流程                          │
└─────────────────────────────────────────────────────────────────┘

用户输入代码
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FastAPI后端 (main.py)                                        │
│  POST /api/review                                             │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│  CodeReviewSystem.review_code()                              │
│  (autogen_reviewer.py)                                       │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐      ┌──────────────┐
│  Architect   │      │  Reviewer    │
│  (架构师)     │      │  (审查员)     │
│              │      │              │
│  - 架构分析   │      │  - Bug检查    │
│  - 设计模式   │      │  - 安全漏洞   │
│  - 模块化评估 │      │  - 编码规范   │
└──────┬───────┘      └──────┬───────┘
       │                      │
       │  架构报告            │  审查报告
       │                      │
       └──────────┬───────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   Optimizer     │
         │   (优化器)      │
         │                 │
         │  - 综合分析     │
         │  - 生成修复代码 │
         │  - 质量评分     │
         └────────┬────────┘
                  │
                  │ 修复代码 + 工具调用指令
                  │ "请 User_Proxy 调用 save_fixed_code..."
                  │
                  ▼
         ┌─────────────────┐
         │  User_Proxy     │
         │  (工具代理)      │
         │                 │
         │  - 接收指令     │
         │  - 调用工具     │
         └────────┬────────┘
                  │
                  │ 执行 save_fixed_code()
                  │
                  ▼
         ┌─────────────────┐
         │  tools.py       │
         │  save_fixed_code│
         │                 │
         │  - 创建fixed/   │
         │  - 保存文件     │
         └────────┬────────┘
                  │
                  │ 保存结果
                  │
                  ▼
         ┌─────────────────┐
         │  fixed/目录     │
         │  [修复文件].py  │
         └─────────────────┘
                  │
                  │ 返回结果
                  │
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  返回JSON响应                                                 │
│  {                                                           │
│    architect_report: "...",                                 │
│    reviewer_report: "...",                                  │
│    optimizer_report: "...",                                 │
│    fixed_code: "...",                                       │
│    save_result: {success: true, saved_path: "..."}         │
│  }                                                           │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│  前端接收结果 (ReviewResults.tsx)                             │
│  - 代码对比视图 (ReactDiffViewer)                            │
│  - 架构分析报告                                               │
│  - 审查报告                                                   │
│  - 优化报告                                                   │
│  - 文件下载功能                                               │
└──────────────────────────────────────────────────────────────┘
```

## 关键文件说明

### ⭐ 核心文件

1. **backend/autogen_reviewer.py**
   - 实现三个智能体的创建和协作
   - 实现 Optimizer 通过 User_Proxy 调用工具的逻辑
   - 核心方法：`review_code()`

2. **backend/tools.py**
   - `save_fixed_code()` 工具函数实现
   - 负责将修复后的代码保存到 `fixed/` 目录

3. **backend/example_optimizer_tool_call.py**
   - 详细展示 Optimizer 如何调用工具的多种方式
   - 包含完整的消息格式示例

4. **frontend/src/components/ReviewResults.tsx**
   - 实现代码差异对比视图
   - 使用 `react-diff-viewer-continued` 组件
   - 支持多标签页切换查看不同报告

## 数据流

```
前端代码输入
    │
    ▼
HTTP POST /api/review
    │
    ▼
CodeReviewSystem.review_code()
    │
    ├─→ Architect.generate_reply() → 架构报告
    ├─→ Reviewer.generate_reply() → 审查报告
    └─→ Optimizer + User_Proxy (GroupChat)
            │
            ├─→ Optimizer生成修复代码
            ├─→ Optimizer指示调用工具
            └─→ User_Proxy执行save_fixed_code()
                    │
                    └─→ 保存到fixed/目录
    │
    ▼
返回JSON响应
    │
    ▼
前端展示结果
    ├─→ Diff View (代码对比)
    ├─→ 架构分析报告
    ├─→ 代码审查报告
    └─→ 优化报告
```

## 技术栈层次

```
┌─────────────────────────────────────────┐
│  前端层 (React + TypeScript)            │
│  - UI组件                                │
│  - 状态管理                              │
│  - API调用                               │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
               ▼
┌─────────────────────────────────────────┐
│  API层 (FastAPI)                        │
│  - RESTful接口                           │
│  - WebSocket支持                         │
│  - 文件上传/下载                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  业务逻辑层 (AutoGen)                    │
│  - 智能体协作                            │
│  - 代码审查流程                          │
│  - 工具调用                              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  AI模型层 (DeepSeek API)                 │
│  - LLM推理                               │
│  - 代码生成                              │
│  - 代码分析                              │
└─────────────────────────────────────────┘
```

## 消息传递格式

### Optimizer → User_Proxy 消息示例

```
修复代码已完成。

## 修复后的代码
```python
[完整代码内容]
```

请 User_Proxy 调用 save_fixed_code 工具保存代码：
- file_path: "example.py"
- fixed_code: [上面的完整代码]
- original_file_name: "example.py"
```

### User_Proxy 工具调用响应

```json
{
  "success": true,
  "saved_path": "fixed/example.py",
  "message": "代码已成功保存到 fixed/example.py"
}
```

## 目录说明

- **backend/**: Python后端服务，包含AutoGen智能体和FastAPI接口
- **frontend/**: React前端应用，提供用户界面和代码对比功能
- **fixed/**: 运行时生成的目录，存储修复后的代码文件

## 扩展点

1. **新增工具函数**: 在 `tools.py` 中添加，并在 `User_Proxy` 中注册
2. **新增智能体**: 在 `autogen_reviewer.py` 中创建，并添加到协作流程
3. **新增前端功能**: 在 `frontend/src/components/` 中添加新组件
4. **新增API接口**: 在 `backend/main.py` 中添加新路由

