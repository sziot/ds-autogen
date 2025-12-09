"""
AutoGen代码审查核心实现
重点展示 Optimizer 如何调用 User_Proxy 的工具函数
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from loguru import logger

from tools import save_fixed_code, TOOL_DESCRIPTIONS


class CodeReviewSystem:
    """代码审查系统 - 核心实现"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 创建智能体
        self.user_proxy = self._create_user_proxy()
        self.architect = self._create_architect()
        self.reviewer = self._create_reviewer()
        self.optimizer = self._create_optimizer()
        
        logger.info("代码审查系统初始化完成")
    
    def _create_user_proxy(self) -> UserProxyAgent:
        """创建用户代理，注册工具函数"""
        user_proxy = UserProxyAgent(
            name="User_Proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config=False,
            system_message="""你是一个工具执行代理。当 Optimizer 请求保存修复后的代码时，
你需要调用 save_fixed_code 工具函数。

工具函数说明：
- save_fixed_code(file_path, fixed_code, original_file_name): 保存修复后的代码到 fixed/ 目录

当 Optimizer 在消息中明确指示调用此工具时，请执行调用。""",
        )
        
        # 注册工具函数
        # 注意：根据AutoGen版本，可能需要使用不同的注册方式
        # 方式1: 如果支持 register_function
        try:
            if hasattr(user_proxy, 'register_function'):
                user_proxy.register_function(
                    function_map={
                        "save_fixed_code": save_fixed_code,
                    }
                )
            # 方式2: 如果支持 register_for_execution
            elif hasattr(user_proxy, 'register_for_execution'):
                user_proxy.register_for_execution(
                    functions=[save_fixed_code]
                )
            # 方式3: 通过 system_message 描述工具，让 LLM 理解如何调用
            # User_Proxy 会在收到指示时手动调用函数
            else:
                logger.warning("AutoGen版本可能不支持自动工具注册，将使用手动调用方式")
        except Exception as e:
            logger.warning(f"工具注册失败，将使用手动调用方式: {str(e)}")
        
        return user_proxy
    
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

输出格式（JSON）：
{
    "architecture_score": 85,
    "design_patterns": ["MVC", "Singleton"],
    "modularity": "良好",
    "issues": ["缺少错误处理模块", "模块耦合度较高"],
    "recommendations": ["引入依赖注入", "拆分大型模块"]
}""",
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

输出格式（JSON）：
{
    "quality_score": 75,
    "bugs": [
        {"line": 10, "severity": "high", "description": "未检查空值"}
    ],
    "security_issues": [
        {"type": "SQL注入", "line": 25, "description": "直接拼接SQL语句"}
    ],
    "code_style_issues": ["缺少类型注解", "函数过长"]
}""",
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
        """创建优化器智能体 - 关键实现"""
        return ConversableAgent(
            name="Optimizer",
            system_message=f"""你是一名代码优化专家，负责根据架构师和审查员的报告生成修复后的代码。

**重要：工具调用说明**

当你完成代码修复后，必须通过以下方式调用 save_fixed_code 工具：

方式1（推荐）：在消息中明确指示 User_Proxy 调用工具
```
我已经完成了代码修复。请 User_Proxy 调用 save_fixed_code 工具保存修复后的代码。

参数：
- file_path: [原始文件路径]
- fixed_code: [完整的修复后代码，包含在代码块中]
- original_file_name: [原始文件名]
```

方式2：使用函数调用格式
如果系统支持函数调用，可以直接调用：
save_fixed_code(
    file_path="...",
    fixed_code="...",
    original_file_name="..."
)

**工作流程：**
1. 接收 Architect 和 Reviewer 的报告
2. 综合分析问题
3. 生成完整的修复后代码（必须是完整可运行的代码）
4. 提供综合质量评分（0-100分）
5. **必须调用 save_fixed_code 工具保存代码**

输出格式：
```
## 修复说明
[详细的修复说明]

## 综合质量评分
[0-100分]

## 修复后的代码
```python
[完整的修复后代码]
```

## 工具调用
请 User_Proxy 执行以下工具调用：
save_fixed_code(
    file_path="[原始路径]",
    fixed_code="[上面的完整代码]",
    original_file_name="[文件名]"
)
```""",
            llm_config={
                "config_list": [{
                    "model": self.model,
                    "api_key": self.api_key,
                    "base_url": self.base_url,
                }],
                "temperature": 0.1,
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
        )
    
    def review_code(
        self,
        code_content: str,
        file_name: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        执行完整的代码审查流程
        
        Args:
            code_content: 代码内容
            file_name: 文件名
            file_path: 文件路径
            
        Returns:
            审查结果
        """
        logger.info(f"开始审查代码: {file_name}")
        
        # 准备审查任务
        review_prompt = f"""请审查以下代码：

文件名: {file_name}
文件路径: {file_path}

代码内容:
```python
{code_content}
```"""
        
        try:
            # 第一步：Architect 分析
            logger.info("Architect 分析架构...")
            architect_msg = f"{review_prompt}\n\n请作为 Architect 分析这段代码的整体架构，输出JSON格式报告。"
            
            # 使用 initiate_chat 进行对话
            architect_chat = self.user_proxy.initiate_chat(
                self.architect,
                message=architect_msg,
                max_turns=1,
            )
            architect_result = architect_chat.chat_history[-1].get("content", "") if architect_chat.chat_history else ""
            
            # 第二步：Reviewer 审查
            logger.info("Reviewer 审查代码...")
            reviewer_msg = f"{review_prompt}\n\n请作为 Reviewer 审查这段代码的质量和安全性，输出JSON格式报告。"
            
            reviewer_chat = self.user_proxy.initiate_chat(
                self.reviewer,
                message=reviewer_msg,
                max_turns=1,
            )
            reviewer_result = reviewer_chat.chat_history[-1].get("content", "") if reviewer_chat.chat_history else ""
            
            # 第三步：Optimizer 生成修复代码并调用工具
            logger.info("Optimizer 生成修复代码...")
            optimizer_msg = f"""基于以下信息生成修复后的代码：

原始代码:
```python
{code_content}
```

Architect 报告:
{architect_result}

Reviewer 报告:
{reviewer_result}

请作为 Optimizer：
1. 综合分析上述报告
2. 生成完整的修复后代码
3. 提供综合质量评分
4. **重要：必须指示 User_Proxy 调用 save_fixed_code 工具保存代码**

工具调用格式：
在生成修复代码后，请明确说明：
"请 User_Proxy 调用 save_fixed_code 工具，参数：
- file_path: \"{file_path}\"
- fixed_code: [你生成的完整修复代码]
- original_file_name: \"{file_name}\""
"""
            
            # 简化为单轮 Optimizer 回复，后端直接保存，避免卡在对话轮询
            optimizer_reply = self.optimizer.generate_reply(
                messages=[{"role": "user", "content": optimizer_msg}]
            ) or ""
            fixed_code = self._extract_code_block(optimizer_reply) or code_content
            save_result = save_fixed_code(
                file_path=file_path,
                fixed_code=fixed_code,
                original_file_name=file_name,
            )
            
            return {
                "architect_report": architect_result,
                "reviewer_report": reviewer_result,
                "optimizer_report": optimizer_reply,
                "fixed_code": fixed_code,
                "save_result": save_result,
                "file_name": file_name,
                "file_path": file_path,
            }
            
        except Exception as e:
            logger.error(f"代码审查出错: {str(e)}")
            raise
    
    def _extract_results_from_chat(self, chat_result) -> tuple:
        """
        从对话结果中提取修复代码和保存结果
        
        Returns:
            (fixed_code, save_result)
        """
        fixed_code = ""
        save_result = None
        
        # 从聊天历史中提取信息
        if hasattr(chat_result, 'chat_history'):
            for msg in reversed(chat_result.chat_history):
                content = msg.get("content", "")
                
                # 提取代码块（支持多种代码块格式）
                code_patterns = [
                    r'```python\n(.*?)\n```',
                    r'```\n(.*?)\n```',
                    r'```(.*?)```',
                ]
                for pattern in code_patterns:
                    code_match = re.search(pattern, content, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1).strip()
                        break
                
                # 检查是否有工具调用结果
                if "save_fixed_code" in content or "保存" in content or "success" in content.lower():
                    # 尝试提取JSON格式的结果
                    json_match = re.search(r'\{[^{}]*"success"[^{}]*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            save_result = json.loads(json_match.group(0))
                        except:
                            # 如果JSON解析失败，尝试手动构建结果
                            if "success" in content.lower() and "true" in content.lower():
                                save_result = {
                                    "success": True,
                                    "message": "代码已保存"
                                }
                            elif "success" in content.lower() and "false" in content.lower():
                                save_result = {
                                    "success": False,
                                    "message": "保存失败"
                                }
        
        return fixed_code, save_result

    @staticmethod
    def _extract_code_block(content: str) -> str:
        """提取回复中的第一个代码块"""
        if not content:
            return ""
        patterns = [
            r"```python\n(.*?)```",
            r"```\n(.*?)```",
            r"```(.*?)```",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""


# 使用示例
def create_review_system(api_key: str, base_url: str) -> CodeReviewSystem:
    """创建代码审查系统实例"""
    return CodeReviewSystem(api_key, base_url)

