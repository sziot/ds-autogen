class OptimizerAgent(AssistantAgent):
    """优化器智能体 - 增强版本"""
    
    async def optimize_code(self, original_code: str, file_name: str, 
                           architect_report: dict, reviewer_report: dict, 
                           options: dict = None):
        """增强的代码优化方法"""
        
        # 新增：智能代码补全
        augmented_code = await self._augment_code_with_context(original_code)
        
        # 构建优化的系统提示
        system_message = self._get_enhanced_system_message(options)
        
        # 使用流式处理生成修复
        fixed_code = await self._streaming_code_fix(
            augmented_code,
            architect_report,
            reviewer_report,
            system_message
        )
        
        # 新增：代码质量自动评分
        quality_score = await self._auto_score_code(fixed_code, original_code)
        
        # 增强的保存机制
        save_result = await self._enhanced_save(
            fixed_code, 
            file_name, 
            quality_score,
            options.get("backup", True)
        )
        
        return {
            "fixed_code": fixed_code,
            "quality_score": quality_score,
            "save_result": save_result,
            "diff_stats": self._calculate_detailed_diff(original_code, fixed_code)
        }
    
    async def _enhanced_save(self, fixed_code: str, file_name: str, 
                            quality_score: float, backup: bool = True):
        """增强的保存功能"""
        import hashlib
        from datetime import datetime
        
        # 生成版本号
        code_hash = hashlib.sha256(fixed_code.encode()).hexdigest()[:8]
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}_{code_hash}"
        
        # 创建版本化文件名
        name_parts = file_name.rsplit('.', 1)
        versioned_name = f"{name_parts[0]}_{version}.{name_parts[1] if len(name_parts) > 1 else 'py'}"
        
        # 调用保存工具
        result = await self.user_proxy.save_fixed_code(
            file_name=versioned_name,
            fixed_content=fixed_code,
            original_file_name=file_name
        )
        
        # 新增：创建备份（如果需要）
        if backup:
            await self._create_backup(fixed_code, file_name, version)
        
        # 新增：记录到审计日志
        await self._log_save_operation(
            file_name=file_name,
            version=version,
            quality_score=quality_score,
            result=result
        )
        
        return {
            **result,
            "version": version,
            "backup_created": backup
        }