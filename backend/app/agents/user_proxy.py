
### `app/agents/user_proxy.py`
```python
"""
用户代理智能体
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from autogen import UserProxyAgent
from loguru import logger

from app.core.config import settings
from app.tools.code_saver import FixedCodeSaver


class UserProxyAgent(UserProxyAgent):
    """自定义用户代理智能体"""
    
    def __init__(
        self,
        task_id: str,
        llm_config: bool = False,
        name: str = "User_Proxy"
    ):
        super().__init__(
            name=name,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            code_execution_config={
                "work_dir": ".",
                "use_docker": False,
                "last_n_messages": 3
            },
            system_message="""你是代码执行代理。你的职责是：
            1. 执行其他智能体请求的工具调用
            2. 处理文件保存操作
            3. 验证代码执行结果
            
            重要：当 Optimizer 请求保存修复后的代码时，你必须调用 save_fixed_code 工具。
            """,
            llm_config=llm_config
        )
        
        self.task_id = task_id
        self.code_saver = FixedCodeSaver()
        
        # 注册工具函数
        self.register_function(
            function_map={
                "save_fixed_code": self.save_fixed_code
            }
        )
    
    async def save_fixed_code(
        self,
        file_name: str,
        fixed_content: str,
        original_file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        保存修复后的代码
        
        Args:
            file_name: 保存的文件名
            fixed_content: 修复后的代码内容
            original_file_name: 原始文件名
            
        Returns:
            保存结果
        """
        logger.info(f"UserProxy: 开始保存修复后的代码 - {file_name}")
        
        try:
            # 验证参数
            if not file_name or not fixed_content:
                raise ValueError("文件名和代码内容不能为空")
            
            # 调用保存工具
            result = await self.code_saver.save_fixed_code(
                task_id=self.task_id,
                file_name=file_name,
                fixed_content=fixed_content,
                original_file_name=original_file_name
            )
            
            logger.info(f"UserProxy: 代码保存成功 - {result['file_path']}")
            
            return result
            
        except Exception as e:
            logger.error(f"UserProxy: 保存代码失败 - {str(e)}")
            raise
    
    async def execute_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数
            
        Returns:
            执行结果
        """
        try:
            logger.info(f"UserProxy: 执行工具调用 - {tool_name}")
            
            if tool_name == "save_fixed_code":
                # 提取参数
                file_name = tool_args.get("file_name", "fixed_code.py")
                fixed_content = tool_args.get("fixed_content", "")
                original_file_name = tool_args.get("original_file_name")
                
                # 执行保存
                return await self.save_fixed_code(
                    file_name=file_name,
                    fixed_content=fixed_content,
                    original_file_name=original_file_name
                )
            
            else:
                raise ValueError(f"未知的工具: {tool_name}")
                
        except Exception as e:
            logger.error(f"UserProxy: 工具调用失败 - {tool_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"工具调用失败: {str(e)}"
            }
    
    def parse_tool_call(self, message: str) -> Optional[Dict[str, Any]]:
        """
        解析工具调用消息
        
        Args:
            message: 消息内容
            
        Returns:
            工具调用信息
        """
        try:
            # 查找工具调用格式
            import re
            
            # 匹配 ```execution ... ``` 格式
            execution_pattern = r'```execution\s*\n(.*?)\n```'
            match = re.search(execution_pattern, message, re.DOTALL | re.IGNORECASE)
            
            if not match:
                return None
            
            execution_content = match.group(1).strip()
            
            # 解析 JSON
            lines = execution_content.split('\n')
            json_start = None
            
            for i, line in enumerate(lines):
                if '{' in line:
                    json_start = i
                    break
            
            if json_start is None:
                return None
            
            json_content = '\n'.join(lines[json_start:])
            
            try:
                tool_call = json.loads(json_content)
                
                # 验证必要的字段
                if not isinstance(tool_call, dict):
                    return None
                
                # 添加任务ID
                tool_call["task_id"] = self.task_id
                
                return tool_call
                
            except json.JSONDecodeError:
                # 尝试修复 JSON
                try:
                    # 移除可能的注释
                    json_content = re.sub(r'//.*', '', json_content)
                    json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
                    
                    tool_call = json.loads(json_content)
                    tool_call["task_id"] = self.task_id
                    return tool_call
                    
                except:
                    return None
                    
        except Exception as e:
            logger.error(f"解析工具调用失败: {str(e)}")
            return None