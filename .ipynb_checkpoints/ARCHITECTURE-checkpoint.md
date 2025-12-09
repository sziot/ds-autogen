# AI代码审查系统 - 系统架构文档

## 系统架构树形图

```
ds-autogen/
├── backend/                          # 后端服务（Python + AutoGen）
│   ├── main.py                      # FastAPI 主服务
│   ├── agents.py                    # AutoGen 智能体定义（旧版）
│   ├── autogen_reviewer.py          # 代码审查核心实现（重点）
│   ├── tools.py                     # 工具函数（save_fixed_code）
│   ├── example_optimizer_tool_call.py # Optimizer工具调用示例
│   ├── requirements.txt             # Python依赖
│   └── .env.example                 # 环境变量示例
│
├── frontend/                         # 前端应用（Vite + React 18 + TypeScript）
│   ├── src/
│   │   ├── main.tsx                 # 应用入口
│   │   ├── App.tsx                  # 主应用组件
│   │   ├── index.css                # 全局样式（浅色主题）
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript类型定义
│   │   ├── services/
│   │   │   └── api.ts               # API服务封装
│   │   └── components/
│   │       ├── CodeUpload.tsx       # 代码上传组件
│   │       └── ReviewResults.tsx    # 审查结果展示组件（含Diff View）
│   ├── index.html                   # HTML入口
│   ├── package.json                 # 前端依赖
│   ├── vite.config.ts               # Vite配置
│   ├── tsconfig.json                # TypeScript配置
│   ├── tailwind.config.js           # Tailwind CSS配置
│   └── postcss.config.js            # PostCSS配置
│
└── README.md                         # 项目说明
```

## 系统架构说明

### 一、后端架构（Python + AutoGen）

#### 1. 核心组件

**1.1 AutoGen 智能体系统**

```
┌─────────────────────────────────────────────────────────┐
│              AutoGen 智能体协作流程                        │
└─────────────────────────────────────────────────────────┘

    [用户代码输入]
           │
           ▼
    ┌─────────────┐
    │  Architect  │  ← 分析代码架构、设计模式、模块化
    │  (架构师)    │
    └──────┬──────┘
           │ 架构报告
           ▼
    ┌─────────────┐
    │  Reviewer   │  ← 检查Bug、安全漏洞、编码规范
    │  (审查员)    │
    └──────┬──────┘
           │ 审查报告
           ▼
    ┌─────────────┐
    │  Optimizer  │  ← 生成修复代码
    │  (优化器)    │
    └──────┬──────┘
           │ 修复代码 + 工具调用指令
           ▼
    ┌─────────────┐
    │ User_Proxy  │  ← 执行 save_fixed_code 工具
    │ (工具代理)   │
    └──────┬──────┘
           │ 保存结果
           ▼
    [fixed/ 目录]
```

**1.2 关键实现：Optimizer → User_Proxy 工具调用**

```python
# 在 autogen_reviewer.py 中实现

# 1. User_Proxy 注册工具
user_proxy.register_function(
    function_map={
        "save_fixed_code": save_fixed_code,
    }
)

# 2. Optimizer 在消息中指示调用工具
optimizer_message = """
修复代码已完成。请 User_Proxy 调用 save_fixed_code 工具：
- file_path: "example.py"
- fixed_code: [完整代码]
- original_file_name: "example.py"
"""

# 3. 通过 GroupChat 实现通信
groupchat = GroupChat(
    agents=[optimizer, user_proxy],
    messages=[],
    max_round=10,
)
```

#### 2. API 接口

```
POST   /api/review              # 代码审查（JSON）
POST   /api/review/upload       # 文件上传审查
GET    /api/download/{filename} # 下载修复后的文件
GET    /api/files               # 列出所有修复文件
WS     /ws/review               # WebSocket实时审查
```

### 二、前端架构（Vite + React 18 + TypeScript）

#### 1. 技术栈

- **构建工具**: Vite 5.x
- **框架**: React 18.3
- **语言**: TypeScript 5.x
- **样式**: Tailwind CSS 3.x
- **代码对比**: react-diff-viewer-continued
- **HTTP客户端**: Axios

#### 2. 组件结构

```
App
├── CodeUpload          # 代码上传区域
│   ├── 文件选择
│   ├── 代码编辑器
│   └── 审查按钮
│
└── ReviewResults       # 审查结果展示
    ├── 代码对比 (Diff View)
    ├── 架构分析报告
    ├── 代码审查报告
    ├── 优化报告
    └── 文件下载
```

#### 3. 数据流

```
用户上传代码
    │
    ▼
CodeUpload 组件
    │
    ▼
API 调用 (reviewCode)
    │
    ▼
后端 AutoGen 处理
    │
    ▼
返回审查结果
    │
    ▼
ReviewResults 组件
    ├── Diff View 展示
    ├── 报告展示
    └── 下载功能
```

## 核心功能实现

### 1. Optimizer 调用工具的关键代码

**位置**: `backend/autogen_reviewer.py`

```python
# Optimizer 的 system_message 中包含工具调用说明
optimizer = ConversableAgent(
    name="Optimizer",
    system_message="""
    当你完成代码修复后，必须通过以下方式调用 save_fixed_code 工具：
    
    方式1（推荐）：在消息中明确指示 User_Proxy 调用工具
    ```
    请 User_Proxy 调用 save_fixed_code 工具保存修复后的代码。
    参数：
    - file_path: [原始文件路径]
    - fixed_code: [完整的修复后代码]
    - original_file_name: [原始文件名]
    ```
    """,
    ...
)

# User_Proxy 注册工具
user_proxy.register_function(
    function_map={
        "save_fixed_code": save_fixed_code,
    }
)

# 通过 GroupChat 实现通信
groupchat = GroupChat(
    agents=[optimizer, user_proxy],
    messages=[],
    max_round=10,
)
```

### 2. 工具函数实现

**位置**: `backend/tools.py`

```python
def save_fixed_code(
    file_path: str,
    fixed_code: str,
    original_file_name: str,
    base_dir: str = "fixed"
) -> Dict[str, Any]:
    """保存修复后的代码到 fixed/ 目录"""
    fixed_dir = Path(base_dir)
    fixed_dir.mkdir(parents=True, exist_ok=True)
    
    save_path = fixed_dir / Path(original_file_name).name
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    return {
        "success": True,
        "saved_path": str(save_path),
        "message": f"代码已成功保存到 {save_path}",
    }
```

### 3. 前端 Diff View 实现

**位置**: `frontend/src/components/ReviewResults.tsx`

```tsx
import ReactDiffViewer from 'react-diff-viewer-continued';

<ReactDiffViewer
  oldValue={originalCode}
  newValue={result.fixed_code}
  splitView={true}
  leftTitle="原始代码"
  rightTitle="修复后代码"
  showDiffOnly={false}
  useDarkTheme={false}  // 浅色主题
/>
```

## 消息传递格式

### Optimizer → User_Proxy 消息格式

```json
{
  "role": "assistant",
  "content": "修复代码已完成。\n\n## 修复后的代码\n```python\n[完整代码]\n```\n\n请 User_Proxy 调用 save_fixed_code 工具：\n- file_path: \"example.py\"\n- fixed_code: [上面的代码]\n- original_file_name: \"example.py\""
}
```

### User_Proxy 工具调用响应

```json
{
  "role": "function",
  "name": "save_fixed_code",
  "content": "{\"success\": true, \"saved_path\": \"fixed/example.py\", \"message\": \"代码已成功保存\"}"
}
```

## 环境配置

### 后端环境变量

```bash
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 前端环境变量（可选）

```bash
VITE_API_URL=http://localhost:8000/api
```

## 部署说明

### 后端启动

```bash
cd backend
pip install -r requirements.txt
# 配置 .env 文件
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 系统特点

1. **智能体协作**: Architect → Reviewer → Optimizer 三阶段审查
2. **自动保存**: Optimizer 通过 User_Proxy 自动保存修复代码
3. **实时对比**: 前端提供代码差异对比视图
4. **浅色主题**: 整体采用浅色主题设计
5. **类型安全**: 前端使用 TypeScript 确保类型安全

## 扩展说明

- 支持 WebSocket 实时通信
- 支持文件上传和下载
- 可扩展更多工具函数
- 支持多种编程语言审查

