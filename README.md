# AI代码审查系统

基于 DeepSeek 大模型和 AutoGen 框架的智能代码审查系统。

## 系统概述

本系统采用前后端分离架构，使用 AutoGen 实现三个智能体（Architect、Reviewer、Optimizer）协作进行代码审查，并自动生成修复后的代码。

### 核心特性

- 🏗️ **架构分析**: Architect 智能体分析代码整体结构和设计模式
- 🔍 **代码审查**: Reviewer 智能体检查 Bug、安全漏洞和编码规范
- ⚡ **自动修复**: Optimizer 智能体生成修复后的代码并自动保存
- 📊 **代码对比**: 前端提供可视化的代码差异对比（Diff View）
- 🎨 **浅色主题**: 整体采用现代化的浅色主题设计

## 技术栈

### 后端
- Python 3.8+
- FastAPI - Web 框架
- AutoGen - 多智能体协作框架
- DeepSeek API - 大语言模型

### 前端
- Vite 5.x - 构建工具
- React 18.3 - UI 框架
- TypeScript 5.x - 类型安全
- Tailwind CSS 3.x - 样式框架
- react-diff-viewer-continued - 代码对比组件

## 快速开始

### 1. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 查看应用。

## 项目结构

```
ds-autogen/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI 主服务
│   ├── autogen_reviewer.py    # 代码审查核心实现
│   ├── tools.py               # 工具函数
│   └── requirements.txt       # Python依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── services/          # API服务
│   │   └── types/             # TypeScript类型
│   └── package.json           # 前端依赖
│
└── ARCHITECTURE.md            # 系统架构文档
```

详细架构说明请查看 [ARCHITECTURE.md](./ARCHITECTURE.md)

## 核心功能说明

### AutoGen 智能体协作流程

1. **Architect（架构师）**: 分析代码整体架构、设计模式和模块化程度
2. **Reviewer（审查员）**: 检查具体 Bug、安全漏洞（XSS、SQL注入等）和编码规范
3. **Optimizer（优化器）**: 根据前两者的报告生成修复后的代码，并通过 User_Proxy 调用工具保存

### Optimizer 工具调用机制

Optimizer 完成代码修复后，会通过以下方式指示 User_Proxy 调用 `save_fixed_code` 工具：

```python
# Optimizer 在消息中明确指示
message = """
修复代码已完成。请 User_Proxy 调用 save_fixed_code 工具：
- file_path: "example.py"
- fixed_code: [完整代码]
- original_file_name: "example.py"
"""
```

详细示例请查看 `backend/example_optimizer_tool_call.py`

## API 接口

### 代码审查

```bash
POST /api/review
Content-Type: application/json

{
  "code": "def hello(): print('Hello')",
  "file_name": "example.py",
  "file_path": "example.py"
}
```

### 文件上传审查

```bash
POST /api/review/upload
Content-Type: multipart/form-data

file: [文件]
```

### 下载修复后的文件

```bash
GET /api/download/{filename}
```

### WebSocket 实时审查

```bash
WS /ws/review

# 发送消息
{
  "type": "review",
  "code": "...",
  "file_name": "example.py"
}
```

## 环境变量

### 后端 (.env)

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 前端 (.env)

```bash
VITE_API_URL=http://localhost:8000/api
```

## 开发说明

### 后端开发

- 主要文件：`backend/autogen_reviewer.py` - 智能体配置和协作逻辑
- 工具函数：`backend/tools.py` - `save_fixed_code` 等工具
- API 服务：`backend/main.py` - FastAPI 路由和 WebSocket

### 前端开发

- 主应用：`frontend/src/App.tsx`
- 代码上传：`frontend/src/components/CodeUpload.tsx`
- 结果展示：`frontend/src/components/ReviewResults.tsx`（含 Diff View）

## 注意事项

1. 确保 DeepSeek API Key 已正确配置
2. 修复后的代码保存在 `backend/fixed/` 目录
3. 前端默认连接到 `http://localhost:8000`
4. 支持多种编程语言（.py, .js, .ts, .java, .cpp 等）

## 许可证

MIT License
