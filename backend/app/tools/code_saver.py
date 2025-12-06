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
    """修复后代码保存器"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.fixed_dir = Path(settings.FIXED_DIR)
        
        # 确保目录存在
        self.upload_dir.mkdir(exist_ok=True, parents=True)
        self.fixed_dir.mkdir(exist_ok=True, parents=True)
    
    async def save_fixed_code(
        self,
        task_id: str,
        file_name: str,
        fixed_content: str,
        original_file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        保存修复后的代码
        
        Args:
            task_id: 任务ID
            file_name: 保存的文件名
            fixed_content: 修复后的代码内容
            original_file_name: 原始文件名
            
        Returns:
            保存结果
        """
        try:
            logger.info(f"开始保存修复后的代码: {file_name}")
            
            # 验证参数
            if not file_name or not fixed_content:
                raise ValueError("文件名和代码内容不能为空")
            
            # 创建任务目录
            task_dir = self.fixed_dir / task_id
            task_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            safe_file_name = self._sanitize_filename(file_name)
            fixed_file_path = task_dir / safe_file_name
            
            # 保存文件
            await self._write_file(fixed_file_path, fixed_content)
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(fixed_file_path)
            
            # 生成元数据
            metadata = {
                "task_id": task_id,
                "file_name": file_name,
                "fixed_file_name": safe_file_name,
                "file_path": str(fixed_file_path),
                "file_hash": file_hash,
                "file_size": len(fixed_content.encode('utf-8')),
                "line_count": fixed_content.count('\n') + 1,
                "saved_at": datetime.utcnow().isoformat(),
                "original_file_name": original_file_name
            }
            
            # 保存元数据
            metadata_path = task_dir / f"{safe_file_name}.meta.json"
            await self._write_json(metadata_path, metadata)
            
            logger.info(f"代码保存成功: {fixed_file_path}")
            
            return {
                "status": "success",
                "message": "修复后的代码已保存",
                "file_path": str(fixed_file_path),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"保存代码失败: {str(e)}")
            raise
    
    async def save_original_code(
        self,
        task_id: str,
        file_name: str,
        original_content: str
    ) -> Dict[str, Any]:
        """
        保存原始代码
        
        Args:
            task_id: 任务ID
            file_name: 文件名
            original_content: 原始代码内容
            
        Returns:
            保存结果
        """
        try:
            logger.info(f"开始保存原始代码: {file_name}")
            
            # 创建任务目录
            task_dir = self.upload_dir / task_id
            task_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            safe_file_name = self._sanitize_filename(file_name)
            original_file_path = task_dir / safe_file_name
            
            # 保存文件
            await self._write_file(original_file_path, original_content)
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(original_file_path)
            
            # 生成元数据
            metadata = {
                "task_id": task_id,
                "file_name": file_name,
                "original_file_name": safe_file_name,
                "file_path": str(original_file_path),
                "file_hash": file_hash,
                "file_size": len(original_content.encode('utf-8')),
                "line_count": original_content.count('\n') + 1,
                "saved_at": datetime.utcnow().isoformat()
            }
            
            # 保存元数据
            metadata_path = task_dir / f"{safe_file_name}.meta.json"
            await self._write_json(metadata_path, metadata)
            
            logger.info(f"原始代码保存成功: {original_file_path}")
            
            return {
                "status": "success",
                "message": "原始代码已保存",
                "file_path": str(original_file_path),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"保存原始代码失败: {str(e)}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        import re
        
        # 移除非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 限制长度
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        
        return filename
    
    async def _write_file(self, file_path: Path, content: str) -> None:
        """写入文件"""
        # 使用异步文件写入
        import aiofiles
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def _write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """写入 JSON 文件"""
        import aiofiles
        import json
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        import aiofiles
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"读取文件失败: {file_path}, {str(e)}")
            raise
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        stat = file_path.stat()
        
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir()
        }
    
    async def cleanup_old_files(self, days: int = 7) -> Dict[str, Any]:
        """
        清理旧文件
        
        Args:
            days: 保留天数
            
        Returns:
            清理结果
        """
        try:
            import shutil
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_files = []
            
            # 清理上传目录
            for task_dir in self.upload_dir.iterdir():
                if task_dir.is_dir():
                    dir_time = datetime.fromtimestamp(task_dir.stat().st_mtime)
                    if dir_time < cutoff_date:
                        shutil.rmtree(task_dir)
                        cleaned_files.append(str(task_dir))
            
            # 清理修复目录
            for task_dir in self.fixed_dir.iterdir():
                if task_dir.is_dir():
                    dir_time = datetime.fromtimestamp(task_dir.stat().st_mtime)
                    if dir_time < cutoff_date:
                        shutil.rmtree(task_dir)
                        cleaned_files.append(str(task_dir))
            
            logger.info(f"清理完成，删除了 {len(cleaned_files)} 个旧目录")
            
            return {
                "status": "success",
                "message": f"清理完成，删除了 {len(cleaned_files)} 个旧目录",
                "cleaned_files": cleaned_files
            }
            
        except Exception as e:
            logger.error(f"清理文件失败: {str(e)}")
            raise