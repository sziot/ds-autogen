"""
优化器智能体
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from autogen import AssistantAgent
from loguru import logger

from app.core.config import settings
from app.agents.user_proxy import UserProxyAgent
from app.tools.code_saver import FixedCodeSaver


@dataclass
class OptimizationResult:
    """优化结果"""
    fixed_code: str
    quality_score: float
    summary: str
    changes: List[Dict[str, Any]]
    file_name: str


class OptimizerAgent(AssistantAgent):
    """优化器智能体"""
    
    def __init__(
        self,
        llm_config: Dict[str, Any],
        task_id: str,
        user_proxy: UserProxyAgent,
        name: str = "Optimizer"
    ):
        super().__init__(
            name=name,
            llm_config=llm_config,
            system_message=self._get_system_message(),
            human_input_mode="NEVER"
        )
        
        self.task_id = task_id
        self.user_proxy = user_proxy
        
        # 注册工具
        self.register_function(
            function_map={
                "save_fixed_code": self._save_fixed_code
            }
        )
    
    def _get_system_message(self) -> str:
        """获取系统消息"""
        return f"""你是一个资深代码优化专家。你的职责是：

1. 综合分析架构师（Architect）和审查员（Reviewer）的报告
2. 生成完整、可直接运行的修复后代码
3. 提供代码质量评分（1-10分）
4. **必须调用工具保存修复后的代码**

## 输入格式
你将收到：
- 原始代码
- 架构分析报告
- 代码审查报告

## 输出要求
1. **修复后的完整代码**：提供可直接运行的完整文件
2. **质量评分**：基于架构、安全、规范的综合性评分
3. **修改说明**：详细说明所做的修改
4. **工具调用**：必须调用 save_fixed_code 保存代码

## 工具调用格式
你必须使用以下格式调用保存工具：

```execution
请调用 save_fixed_code 工具：
{{
    "task_id": "{self.task_id}",
    "file_name": "修复后的文件名.py",
    "fixed_content": "完整的修复后代码",
    "original_file_name": "原始文件名.py"
}}