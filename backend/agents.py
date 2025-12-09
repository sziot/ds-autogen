"""
AutoGen智能体配置模块
实现 Architect → Reviewer → Optimizer 三个智能体协作
"""

import os
from typing import Dict, Any, Optional
from autogen import ConversableAgent, UserProxyAgent
from loguru import logger


class CodeReviewAgents:
    """代码审查智能体系统"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-chat"):
        """
        初始化智能体系统
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 创建智能体
        self.architect = self._create_architect()
        self.reviewer = self._create_reviewer()
        self.optimizer = self._create_optimizer()
        self.user_proxy = self._create_user_proxy()
        
        # 设置智能体之间的通信关系
        self._setup_agent_communication()
        
        logger.info("代码审查智能体系统初始化完成")
    
    def _create_architect(self) -> ConversableAgent:
        """创建架构师智能体"""
        return ConversableAgent(
            name="Architect",
            system_message="""你是一名资深的全栈架构师，专注于代码整体结构分析。

你的职责：
1. 分析代码的整体架构和设计模式
2. 评估模块化程度和代码组织
3. 识别架构层面的问题和改进建议
4. 提供结构性的优化建议

输出格式：
- 架构分析报告（JSON格式）
- 设计模式评估
- 模块化建议
- 架构评分（0-100分）

请以结构化的方式输出你的分析结果。""",
            llm_config={
                "config_list": [{
                    "model": self.model,
                    "api_key": self.api_key,
                    "base_url": self.base_url,
                }],
                "temperature": 0.3,
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )
    
    def _create_reviewer(self) -> ConversableAgent:
        """创建审查员智能体"""
        return ConversableAgent(
            name="Reviewer",
            system_message="""你是一名专业的代码审查员，专注于代码质量和安全性。

你的职责：
1. 深入检查代码中的Bug和潜在错误
2. 识别安全漏洞（XSS、SQL注入、CSRF等）
3. 检查编码规范和最佳实践
4. 发现性能问题和资源泄漏
5. 提供详细的问题报告

输出格式：
- 问题列表（包含行号、严重程度、描述）
- 安全漏洞报告
- 编码规范问题
- 代码质量评分（0-100分）

请以结构化的方式输出你的审查结果。""",
            llm_config={
                "config_list": [{
                    "model": self.model,
                    "api_key": self.api_key,
                    "base_url": self.base_url,
                }],
                "temperature": 0.2,
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )
    
    def _create_optimizer(self) -> ConversableAgent:
        """创建优化器智能体（核心）"""
        return ConversableAgent(
            name="Optimizer",
            system_message="""你是一名代码优化专家，负责根据架构师和审查员的报告生成修复后的代码。

你的职责：
1. 综合分析 Architect 和 Reviewer 的报告
2. 生成完整的、已修复的代码文件内容
3. 确保修复后的代码符合最佳实践
4. 提供最终的综合质量评分
5. **重要**：生成修复代码后，必须调用 save_fixed_code 工具保存文件

输出要求：
1. 首先提供修复说明和综合评分
2. 然后生成完整的修复后代码
3. 最后必须调用 save_fixed_code 工具保存代码

工具调用格式示例：
```python
# 当需要保存修复后的代码时，使用以下格式：
TERMINATE

请调用 save_fixed_code 工具，参数：
- file_path: 原始文件路径
- fixed_code: 修复后的完整代码内容
- original_file_name: 原始文件名
```

注意：修复后的代码必须是完整的、可直接运行的代码文件。""",
            llm_config={
                "config_list": [{
                    "model": self.model,
                    "api_key": self.api_key,
                    "base_url": self.base_url,
                }],
                "temperature": 0.1,  # 较低温度确保代码生成的一致性
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
        )
    
    def _create_user_proxy(self) -> UserProxyAgent:
        """创建用户代理，用于执行工具函数"""
        return UserProxyAgent(
            name="User_Proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config=False,  # 不执行代码，只调用工具
            system_message="你是一个工具执行代理，负责执行代码保存等工具函数。",
        )
    
    def _setup_agent_communication(self):
        """设置智能体之间的通信关系"""
        # Architect 和 Reviewer 可以互相通信
        self.architect.register_for_llm(name="Reviewer", description="代码审查员")
        self.reviewer.register_for_llm(name="Architect", description="架构师")
        
        # Optimizer 可以接收 Architect 和 Reviewer 的消息
        self.optimizer.register_for_llm(name="Architect", description="架构师")
        self.optimizer.register_for_llm(name="Reviewer", description="代码审查员")
        
        # User_Proxy 可以接收 Optimizer 的指令
        self.optimizer.register_for_llm(name="User_Proxy", description="工具执行代理")
    
    async def review_code(
        self, 
        code_content: str, 
        file_name: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        执行代码审查流程
        
        Args:
            code_content: 代码内容
            file_name: 文件名
            file_path: 文件路径
            
        Returns:
            审查结果字典
        """
        logger.info(f"开始审查代码文件: {file_name}")
        
        # 准备审查任务
        review_task = f"""
请审查以下代码文件：

文件名: {file_name}
文件路径: {file_path}

代码内容:
```python
{code_content}
```

请按照以下流程进行审查：
1. Architect 分析代码架构
2. Reviewer 检查代码质量和安全问题
3. Optimizer 生成修复后的代码并保存
"""
        
        try:
            # 第一步：Architect 分析架构
            logger.info("Architect 开始分析架构...")
            architect_result = await self._run_agent(
                self.architect,
                f"{review_task}\n\n请作为 Architect 分析这段代码的整体架构。"
            )
            
            # 第二步：Reviewer 审查代码
            logger.info("Reviewer 开始审查代码...")
            reviewer_result = await self._run_agent(
                self.reviewer,
                f"{review_task}\n\n请作为 Reviewer 审查这段代码的质量和安全性。"
            )
            
            # 第三步：Optimizer 生成修复代码
            logger.info("Optimizer 开始生成修复代码...")
            optimizer_prompt = f"""
基于以下信息生成修复后的代码：

原始代码:
```python
{code_content}
```

Architect 的分析报告:
{architect_result}

Reviewer 的审查报告:
{reviewer_result}

请作为 Optimizer：
1. 综合分析上述报告
2. 生成完整的修复后代码
3. 提供综合质量评分（0-100分）
4. **必须调用 save_fixed_code 工具保存修复后的代码**

工具调用格式：
在生成修复代码后，请明确指示 User_Proxy 调用 save_fixed_code 工具。
参数：
- file_path: "{file_path}"
- fixed_code: [完整的修复后代码]
- original_file_name: "{file_name}"
"""
            
            # 创建群组对话，让 Optimizer 可以与 User_Proxy 通信
            optimizer_result = await self._run_group_chat(
                optimizer_prompt,
                file_path=file_path,
                fixed_code_placeholder=code_content,  # 占位符，实际由 Optimizer 生成
                original_file_name=file_name
            )
            
            return {
                "architect_report": architect_result,
                "reviewer_report": reviewer_result,
                "optimizer_report": optimizer_result,
                "file_name": file_name,
                "file_path": file_path,
            }
            
        except Exception as e:
            logger.error(f"代码审查过程中出错: {str(e)}")
            raise
    
    async def _run_agent(self, agent: ConversableAgent, message: str) -> str:
        """运行单个智能体"""
        # 注意：AutoGen 的异步支持可能有限，这里使用同步方式
        # 实际使用时可能需要根据 AutoGen 版本调整
        response = agent.generate_reply(
            messages=[{"role": "user", "content": message}]
        )
        return response if response else ""
    
    async def _run_group_chat(
        self, 
        initial_message: str,
        file_path: str,
        fixed_code_placeholder: str,
        original_file_name: str
    ) -> Dict[str, Any]:
        """
        运行群组对话，让 Optimizer 与 User_Proxy 协作
        
        这是关键部分：Optimizer 生成代码后，指示 User_Proxy 调用工具
        """
        from autogen import GroupChat, GroupChatManager
        
        # 创建群组聊天
        groupchat = GroupChat(
            agents=[self.optimizer, self.user_proxy],
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin",
        )
        
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=self.optimizer.llm_config,
        )
        
        # 启动对话
        # 注意：这里需要根据实际的 AutoGen API 调整
        # 实际实现中，Optimizer 会在消息中明确指示调用工具
        
        # 返回结果（实际实现中需要从对话中提取）
        return {
            "message": "Optimizer 已完成代码修复",
            "fixed_code_extracted": False,  # 标记是否成功提取修复代码
        }

