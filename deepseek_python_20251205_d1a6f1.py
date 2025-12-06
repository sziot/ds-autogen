def run_code_review(file_path: str):
    """执行完整的代码审查流程"""
    
    # 1. 创建智能体
    user_proxy, architect, reviewer, optimizer = create_code_review_agents()
    
    # 2. 读取源代码
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 3. 初始化任务
    init_message = f"""
    开始代码审查任务：
    
    文件: {file_path}
    代码内容:
    ```python
    {source_code}
    ```
    
    请按照以下流程执行：
    1. Architect 分析代码架构
    2. Reviewer 审查代码问题
    3. Optimizer 生成修复版本并保存
    """
    
    # 4. 配置群聊
    groupchat = GroupChat(
        agents=[user_proxy, architect, reviewer, optimizer],
        messages=[],
        max_round=10,
        speaker_selection_method="round_robin"
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    # 5. 启动协作
    user_proxy.initiate_chat(
        manager,
        message=init_message
    )
    
    # 6. 提取最终结果
    return extract_results(groupchat.messages)


def extract_results(messages: List[Dict]) -> Dict:
    """从对话历史中提取结果"""
    results = {
        "architect_report": "",
        "reviewer_report": "",
        "optimized_code": "",
        "score": 0,
        "saved_file": ""
    }
    
    for msg in messages:
        content = msg.get("content", "")
        sender = msg.get("name", "")
        
        if sender == "Architect":
            results["architect_report"] = content
        elif sender == "Reviewer":
            results["reviewer_report"] = content
        elif sender == "Optimizer":
            # 提取优化后的代码
            if "```python" in content:
                code_start = content.find("```python") + 9
                code_end = content.find("```", code_start)
                results["optimized_code"] = content[code_start:code_end].strip()
            
            # 提取质量评分
            if "质量评分" in content or "Score:" in content:
                import re
                score_match = re.search(r'(\d+\.?\d*)/10', content)
                if score_match:
                    results["score"] = float(score_match.group(1))
        
        elif sender == "User_Proxy" and "save_fixed_code" in str(msg):
            # 提取保存结果
            if "function_call" in msg:
                func_call = msg["function_call"]
                if func_call.get("name") == "save_fixed_code":
                    args = json.loads(func_call.get("arguments", "{}"))
                    results["saved_file"] = args.get("file_path", "")
    
    return results