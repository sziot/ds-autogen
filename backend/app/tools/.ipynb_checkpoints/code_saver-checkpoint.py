"""
代码保存工具
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from loguru import logger

from app.core.config import settings

class FixedCodeSaver:
    """增强的代码保存器"""
    
    async def save_fixed_code(self, task_id: str, file_name: str, 
                             fixed_content: str, original_file_name: str = None):
        """增强的保存方法"""
        
        # 新增：代码消毒和安全检查
        sanitized_content = await self._sanitize_code(fixed_content)
        
        # 新增：自动格式化（如果配置了格式化工具）
        if self.auto_format:
            formatted_content = await self._auto_format_code(sanitized_content)
        else:
            formatted_content = sanitized_content
        
        # 新增：代码复杂度分析
        complexity_report = await self._analyze_complexity(formatted_content)
        
        # 保存文件（原有逻辑，但使用格式化后的内容）
        save_result = await self._save_to_disk(
            task_id, file_name, formatted_content, original_file_name
        )
        
        # 新增：创建符号链接到最新版本
        await self._create_latest_symlink(task_id, file_name)
        
        # 新增：更新文件索引
        await self._update_file_index(task_id, file_name, save_result["file_path"])
        
        return {
            **save_result,
            "complexity_report": complexity_report,
            "formatted": self.auto_format,
            "sanitized": True
        }
    
    async def _sanitize_code(self, code: str) -> str:
        """代码消毒和安全检查"""
        import re
        
        # 移除潜在的危险模式
        dangerous_patterns = [
            r'__import__\s*\(',  # 动态导入
            r'eval\s*\(',        # eval调用
            r'exec\s*\(',        # exec调用
            r'os\.system\s*\(',  # 系统命令
            r'subprocess\.call'  # 子进程调用
        ]
        
        sanitized = code
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '# SECURITY: Removed dangerous pattern', 
                             sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    async def _auto_format_code(self, code: str) -> str:
        """自动代码格式化"""
        try:
            import black
            import tempfile
            
            # 使用black格式化代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                
                # 运行black格式化
                result = black.format_file_in_place(
                    Path(tmp.name),
                    fast=False,
                    mode=black.FileMode(),
                    write_back=black.WriteBack.YES
                )
                
                # 读取格式化后的内容
                with open(tmp.name, 'r') as f:
                    formatted = f.read()
                
                # 清理临时文件
                Path(tmp.name).unlink()
                
                return formatted
        except Exception as e:
            logger.warning(f"代码格式化失败: {e}")
            return code  # 返回原始代码