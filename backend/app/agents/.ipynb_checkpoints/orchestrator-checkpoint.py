from autogen import GroupChat, GroupChatManager  # 新增导入
from transformers import pipeline  # 新增AI模型支持

class AgentOrchestrator:
    """智能体编排器 - 增强版本"""
    
    def __init__(self, task_id: str):
        # 新增AI模型初始化
        self.code_model = pipeline(
            "text-generation",
            model="deepseek-ai/deepseek-coder-6.7b-instruct",  # 可配置的模型
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        # 增强的WebSocket通信
        self.ws_manager = get_websocket_manager()
        self.message_queue = asyncio.Queue()
        
    async def review_code(self, file_content: str, file_name: str, options: dict):
        """增强的审查流程"""
        # 1. 预处理代码
        processed_code = await self._preprocess_code(file_content)
        
        # 2. 并行执行架构师和审查员分析
        architect_task = asyncio.create_task(
            self._run_architect_analysis(processed_code, file_name, options)
        )
        reviewer_task = asyncio.create_task(
            self._run_code_review(processed_code, file_name, options)
        )
        
        # 等待两个任务完成
        architect_result, reviewer_result = await asyncio.gather(
            architect_task, reviewer_task
        )
        
        # 3. 使用AI模型增强分析
        ai_insights = await self._get_ai_insights(
            processed_code, 
            architect_result, 
            reviewer_result
        )
        
        # 4. 优化器处理（集成AI建议）
        optimizer_result = await self._run_optimization(
            processed_code,
            file_name,
            {**architect_result, **reviewer_result, "ai_insights": ai_insights},
            options
        )
        
        # 5. 验证和保存
        validation_result = await self._validate_fix(optimizer_result["fixed_code"])
        
        return {
            **optimizer_result,
            "validation": validation_result,
            "ai_insights": ai_insights
        }
    
    async def _get_ai_insights(self, code: str, arch_result: dict, rev_result: dict):
        """使用AI模型获取深度见解"""
        prompt = f"""
        分析以下代码并提供改进建议：
        
        代码：
        ```python
        {code[:2000]}  # 限制长度
        ```
        
        架构分析：{json.dumps(arch_result)}
        审查结果：{json.dumps(rev_result)}
        
        请提供：
        1. 潜在的性能问题
        2. 安全增强建议
        3. 代码结构优化
        """
        
        try:
            response = self.code_model(
                prompt,
                max_length=500,
                temperature=0.3,
                num_return_sequences=1
            )
            return response[0]["generated_text"]
        except Exception as e:
            logger.warning(f"AI分析失败: {e}")
            return "AI分析暂时不可用"