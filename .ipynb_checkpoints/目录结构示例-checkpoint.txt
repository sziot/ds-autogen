project/
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── stores/
│   └── vite.config.ts
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── agents/             # AutoGen 智能体
│   │   ├── tools/              # 工具函数
│   │   └── routers/            # API 路由
│   └── main.py
├── fixed/                       # 修复代码目录（自动生成）
│   ├── user_1_project/
│   └── user_2_project/
├── uploads/                     # 上传代码目录
└── docker-compose.yml          # 容器编排