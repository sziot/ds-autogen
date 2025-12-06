from typing import Dict, List, Any, Optional
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
import json

class FixedCodeSaver:
    """工具类：保存修复后的代码"""
    
    @staticmethod
    def save_fixed_code(
        file_path: str,
        fixed_content: str,
        original_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        保存修复后的代码到 fixed/ 目录
        
        Args:
            file_path: 目标保存路径（相对路径）
            fixed_content: 修复后的完整代码内容
            original_path: 原始文件路径（可选）
            
        Returns:
            Dict: 保存结果信息
        """
        try:
            # 确保 fixed 目录存在
            os.makedirs('fixed', exist_ok=True)
            
            # 构建保存路径
            if original_path:
                # 保持原始文件结构
                rel_path = os.path.relpath(original_path)
                save_path = os.path.join('fixed', rel_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
            else:
                # 直接保存到 fixed 目录
                save_path = os.path.join('fixed', os.path.basename(file_path))
            
            # 写入文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return {
                "status": "success",
                "message": f"修复后的代码已保存到: {save_path}",
                "file_path": save_path,
                "size": len(fixed_content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存失败: {str(e)}"
            }