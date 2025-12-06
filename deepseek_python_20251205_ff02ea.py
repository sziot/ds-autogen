def create_code_review_agents():
    """创建 A.R.O. 智能体协作系统"""
    
    # 配置 LLM
    llm_config = {
        "config_list": [
            {
                "model": "deepseek-coder",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com"
            }
        ],
        "temperature": 0.1,
        "timeout": 120
    }
    
    # 1. User Proxy Agent（工具执行器）
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        code_execution_config={
            "work_dir": ".",
            "use_docker": False,
            "last_n_messages": 3
        },
        system_message="""你是一个代码执行代理。你的职责是：
        1. 执行其他智能体请求的工具调用
        2. 处理文件保存操作
        3. 验证代码执行结果
        
        重要：当 Optimizer 请求保存修复后的代码时，你必须调用 save_fixed_code 工具。
        """,
        llm_config=False  # UserProxy 不使用 LLM
    )
    
    # 2. Architect Agent（架构师）
    architect = AssistantAgent(
        name="Architect",
        llm_config=llm_config,
        system_message="""你是一个资深软件架构师。你的职责：
        1. 分析代码整体结构和设计模式
        2. 评估模块化和可扩展性
        3. 提供架构改进建议
        4. 生成架构评估报告
        
        输出格式：
        ## 架构评估报告
        - 整体结构: [评估]
        - 设计模式: [分析]
        - 模块化: [评分]
        - 改进建议: [具体建议]
        """
    )
    
    # 3. Reviewer Agent（审查员）
    reviewer = AssistantAgent(
        name="Reviewer",
        llm_config=llm_config,
        system_message="""你是一个资深代码审查员。你的职责：
        1. 检查具体 Bug 和逻辑错误
        2. 识别安全漏洞（XSS, SQL注入等）
        3. 验证编码规范和最佳实践
        4. 生成详细的问题清单
        
        输出格式：
        ## 代码审查报告
        - 严重问题: [列表]
        - 安全问题: [列表]
        - 规范问题: [列表]
        - 优化建议: [列表]
        """
    )
    
    # 4. Optimizer Agent（优化器） - 核心
    optimizer = AssistantAgent(
        name="Optimizer",
        llm_config=llm_config,
        system_message="""你是一个代码优化专家。你的职责：
        1. 综合 Architect 和 Reviewer 的报告
        2. 生成完整修复后的代码文件
        3. 提供最终质量评分（1-10分）
        4. 关键：必须请求 User_Proxy 保存修复后的代码
        
        工作流程：
        1. 接收 Architect 和 Reviewer 的报告
        2. 生成修复方案
        3. 输出完整的修复后代码
        4. 调用工具保存代码
        
        必须使用以下格式调用保存工具：
        
        ```execution_instruction
        请 User_Proxy 执行 save_fixed_code 工具：
        {
            "file_path": "修复后的文件名.py",
            "fixed_content": "完整的修复后代码",
            "original_path": "原始文件路径（可选）"
        }
        ```
        
        然后提供质量评分和总结。
        """,
        function_map={
            "save_fixed_code": FixedCodeSaver.save_fixed_code
        }
    )
    
    # 注册工具到 UserProxy
    user_proxy.register_function(
        function_map={
            "save_fixed_code": FixedCodeSaver.save_fixed_code
        }
    )
    
    return user_proxy, architect, reviewer, optimizer