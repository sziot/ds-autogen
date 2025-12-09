"""
工具函数模块
包含 save_fixed_code 等工具函数
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


def save_fixed_code(
    file_path: str,
    fixed_code: str,
    original_file_name: str,
    base_dir: str = "fixed"
) -> Dict[str, Any]:
    """
    保存修复后的代码到 fixed/ 目录
    
    Args:
        file_path: 原始文件路径
        fixed_code: 修复后的代码内容
        original_file_name: 原始文件名
        
    Returns:
        保存结果字典
    """
    try:
        # 创建 fixed 目录（如果不存在）
        fixed_dir = Path(base_dir)
        fixed_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成保存路径
        # 如果 original_file_name 包含路径，只取文件名
        safe_filename = Path(original_file_name).name
        save_path = fixed_dir / safe_filename
        
        # 保存文件
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        logger.info(f"修复后的代码已保存到: {save_path}")
        
        return {
            "success": True,
            "saved_path": str(save_path),
            "message": f"代码已成功保存到 {save_path}",
        }
        
    except Exception as e:
        logger.error(f"保存修复代码时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"保存失败: {str(e)}",
        }


def register_tools_to_user_proxy(user_proxy) -> None:
    """
    向 User_Proxy 注册工具函数
    
    Args:
        user_proxy: UserProxyAgent 实例
    """
    # 注册 save_fixed_code 工具
    user_proxy.register_function(
        function_map={
            "save_fixed_code": save_fixed_code,
        }
    )
    
    logger.info("工具函数已注册到 User_Proxy")


# 工具函数描述（用于 LLM 理解工具功能）
TOOL_DESCRIPTIONS = {
    "save_fixed_code": {
        "name": "save_fixed_code",
        "description": "保存修复后的代码文件到 fixed/ 目录",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "原始文件的路径"
                },
                "fixed_code": {
                    "type": "string",
                    "description": "修复后的完整代码内容"
                },
                "original_file_name": {
                    "type": "string",
                    "description": "原始文件名"
                }
            },
            "required": ["file_path", "fixed_code", "original_file_name"]
        }
    }
}

