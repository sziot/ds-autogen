极简方案，前端只有一个index.html文件  
模拟的审核流程 mock_code_review_pipline  
  
启动：  
cd backend  
python main.py  
cd frontend  
python -m http.server 8080  
访问 http://localhost:8080  
  
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
    │   │   └── review_simple.py    # 简化路由模拟的审核流程mock  
    │   └── websocket_manager.py    # WebSocket管理  
    └── utils/                # 工具函数（可选）  
