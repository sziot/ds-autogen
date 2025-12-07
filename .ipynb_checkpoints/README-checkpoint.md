代码审查系统
简化版，不连数据库

项目结构
deepseek-code-review/
├── main.py                    # 主应用文件
├── requirements.txt           # 依赖文件
├── .env                      # 环境变量
├── uploads/                  # 上传文件目录
├── fixed/                    # 修复后文件目录
└── app/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   └── config.py         # 配置管理
    ├── memory_store.py       # 内存存储系统
    ├── services/
    │   └── task_service_memory.py  # 任务服务
    ├── api/
    │   ├── __init__.py
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   └── review_simple.py    # 简化路由
    │   └── websocket_manager.py    # WebSocket管理
    └── utils/                # 工具函数（可选）