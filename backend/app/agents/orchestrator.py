"""
智能体编排器
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from loguru import logger

from app.core.config import settings
from app.agents.architect import ArchitectAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.optimizer import OptimizerAgent
from app.agents.user_proxy import UserProxyAgent
from app.services.llm_service import LLMService
from app.api.websocket_manager import get_websocket_manager
from app.models.schemas import CodeReviewResult, AgentStatus


class AgentStep(Enum):
    """智能体步骤"""
    INITIALIZED = "initialized"
    ARCHITECT_ANALYZING = "architect_analyzing"
    REVIEWER_CHECKING = "reviewer_checking"
    OPTIMIZER_FIXING = "optimizer_fixing"
    SAVING_RESULTS = "saving_results"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentProgress:
    """智能体进度"""
    step: AgentStep
    progress: float  # 0-100
    message: str
    data: Optional[Dict[str, Any]] = None


class AgentOrchestrator:
    """智能体编排器"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.llm_service = LLMService()
        self.ws_manager = get_websocket_manager()
        
        # 智能体实例
        self.architect: Optional[ArchitectAgent] = None
        self.reviewer: Optional[ReviewerAgent] = None
        self.optimizer: Optional[OptimizerAgent] = None
        self.user_proxy: Optional[UserProxyAgent] = None
        
        # 进度跟踪
        self.current_progress = AgentProgress(
            step=AgentStep.INITIALIZED,
            progress=0,
            message="初始化智能体"
        )
    
    async def review_code(
        self,
        file_content: str,
        file_name: str,
        options: Dict[str, Any]
    ) -> CodeReviewResult:
        """
        执行代码审查
        
        Args:
            file_content: 文件内容
            file_name: 文件名
            options: 审查选项
            
        Returns:
            审查结果
        """
        try:
            # 更新进度
            await self._update_progress(
                AgentStep.INITIALIZED,
                5,
                "初始化审查环境"
            )
            
            # 初始化智能体
            await self._initialize_agents()
            
            # 发送初始化通知
            await self._notify_agent_status("initialized", "系统初始化完成")
            
            # 1. 架构分析
            await self._update_progress(
                AgentStep.ARCHITECT_ANALYZING,
                20,
                "开始架构分析"
            )
            
            architect_result = await self._run_architect_analysis(
                file_content, file_name, options
            )
            
            # 2. 代码审查
            await self._update_progress(
                AgentStep.REVIEWER_CHECKING,
                40,
                "开始代码审查"
            )
            
            reviewer_result = await self._run_code_review(
                file_content, file_name, options, architect_result
            )
            
            # 3. 优化修复
            await self._update_progress(
                AgentStep.OPTIMIZER_FIXING,
                60,
                "开始代码优化"
            )
            
            optimizer_result = await self._run_optimization(
                file_content, file_name, options, architect_result, reviewer_result
            )
            
            # 4. 保存结果
            await self._update_progress(
                AgentStep.SAVING_RESULTS,
                80,
                "保存修复结果"
            )
            
            saved_file_info = await self._save_results(optimizer_result)
            
            # 5. 完成
            await self._update_progress(
                AgentStep.COMPLETED,
                100,
                "代码审查完成"
            )
            
            # 生成最终结果
            result = self._generate_final_result(
                file_content=file_content,
                file_name=file_name,
                architect_result=architect_result,
                reviewer_result=reviewer_result,
                optimizer_result=optimizer_result,
                saved_file_info=saved_file_info
            )
            
            return result
            
        except Exception as e:
            logger.error(f"代码审查失败: {str(e)}", exc_info=True)
            
            await self._update_progress(
                AgentStep.FAILED,
                0,
                f"审查失败: {str(e)}"
            )
            
            raise
    
    async def _initialize_agents(self):
        """初始化智能体"""
        try:
            # 初始化 LLM 配置
            llm_config = {
                "config_list": [
                    {
                        "model": settings.DEEPSEEK_MODEL,
                        "api_key": settings.DEEPSEEK_API_KEY,
                        "api_base": settings.DEEPSEEK_BASE_URL,
                        "api_type": "open_ai"
                    }
                ],
                "temperature": settings.AI_TEMPERATURE,
                "timeout": settings.AI_TIMEOUT,
                "max_tokens": settings.AI_MAX_TOKENS,
            }
            
            # 创建智能体
            self.user_proxy = UserProxyAgent(
                task_id=self.task_id,
                llm_config=False
            )
            
            self.architect = ArchitectAgent(
                llm_config=llm_config,
                task_id=self.task_id
            )
            
            self.reviewer = ReviewerAgent(
                llm_config=llm_config,
                task_id=self.task_id
            )
            
            self.optimizer = OptimizerAgent(
                llm_config=llm_config,
                task_id=self.task_id,
                user_proxy=self.user_proxy
            )
            
            logger.info(f"智能体初始化完成: {self.task_id}")
            
            # 发送智能体初始化通知
            await self._notify_agent_status(
                "initialized",
                "所有智能体已就绪"
            )
            
        except Exception as e:
            logger.error(f"智能体初始化失败: {str(e)}")
            raise
    
    async def _run_architect_analysis(
        self,
        file_content: str,
        file_name: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        运行架构分析
        
        Args:
            file_content: 文件内容
            file_name: 文件名
            options: 审查选项
            
        Returns:
            架构分析结果
        """
        try:
            # 发送智能体状态通知
            await self._notify_agent_status(
                "Architect",
                "开始架构分析",
                0
            )
            
            # 执行架构分析
            result = await self.architect.analyze_architecture(
                code=file_content,
                file_name=file_name,
                options=options
            )
            
            # 更新进度
            await self._notify_agent_status(
                "Architect",
                "架构分析完成",
                100
            )
            
            # 发送结果通知
            await self.ws_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "agent_update",
                    "data": {
                        "agent": "Architect",
                        "type": "result",
                        "result": result
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"架构分析失败: {str(e)}")
            
            await self._notify_agent_status(
                "Architect",
                f"架构分析失败: {str(e)}",
                0
            )
            
            raise
    
    async def _run_code_review(
        self,
        file_content: str,
        file_name: str,
        options: Dict[str, Any],
        architect_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        运行代码审查
        
        Args:
            file_content: 文件内容
            file_name: 文件名
            options: 审查选项
            architect_result: 架构分析结果
            
        Returns:
            代码审查结果
        """
        try:
            # 发送智能体状态通知
            await self._notify_agent_status(
                "Reviewer",
                "开始代码审查",
                0
            )
            
            # 执行代码审查
            result = await self.reviewer.review_code(
                code=file_content,
                file_name=file_name,
                architect_feedback=architect_result,
                options=options
            )
            
            # 更新进度
            await self._notify_agent_status(
                "Reviewer",
                "代码审查完成",
                100
            )
            
            # 发送结果通知
            await self.ws_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "agent_update",
                    "data": {
                        "agent": "Reviewer",
                        "type": "result",
                        "result": result
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"代码审查失败: {str(e)}")
            
            await self._notify_agent_status(
                "Reviewer",
                f"代码审查失败: {str(e)}",
                0
            )
            
            raise
    
    async def _run_optimization(
        self,
        file_content: str,
        file_name: str,
        options: Dict[str, Any],
        architect_result: Dict[str, Any],
        reviewer_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        运行代码优化
        
        Args:
            file_content: 原始代码
            file_name: 文件名
            options: 审查选项
            architect_result: 架构分析结果
            reviewer_result: 代码审查结果
            
        Returns:
            优化结果
        """
        try:
            # 发送智能体状态通知
            await self._notify_agent_status(
                "Optimizer",
                "开始代码优化",
                0
            )
            
            # 执行代码优化
            result = await self.optimizer.optimize_code(
                original_code=file_content,
                file_name=file_name,
                architect_report=architect_result,
                reviewer_report=reviewer_result,
                options=options
            )
            
            # 更新进度
            await self._notify_agent_status(
                "Optimizer",
                "代码优化完成",
                100
            )
            
            # 发送结果通知
            await self.ws_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "agent_update",
                    "data": {
                        "agent": "Optimizer",
                        "type": "result",
                        "result": result
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"代码优化失败: {str(e)}")
            
            await self._notify_agent_status(
                "Optimizer",
                f"代码优化失败: {str(e)}",
                0
            )
            
            raise
    
    async def _save_results(self, optimizer_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存优化结果
        
        Args:
            optimizer_result: 优化结果
            
        Returns:
            保存的文件信息
        """
        try:
            # 发送智能体状态通知
            await self._notify_agent_status(
                "User_Proxy",
                "开始保存结果",
                0
            )
            
            # 从优化结果中提取修复后的代码
            fixed_code = optimizer_result.get("fixed_code", "")
            if not fixed_code:
                raise ValueError("优化结果中没有找到修复后的代码")
            
            # 使用 UserProxy 保存文件
            file_info = await self.user_proxy.save_fixed_code(
                file_content=fixed_code,
                file_name=optimizer_result.get("file_name", "fixed_code.py"),
                task_id=self.task_id
            )
            
            # 更新进度
            await self._notify_agent_status(
                "User_Proxy",
                "结果保存完成",
                100
            )
            
            return file_info
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")
            
            await self._notify_agent_status(
                "User_Proxy",
                f"保存结果失败: {str(e)}",
                0
            )
            
            raise
    
    def _generate_final_result(
        self,
        file_content: str,
        file_name: str,
        architect_result: Dict[str, Any],
        reviewer_result: Dict[str, Any],
        optimizer_result: Dict[str, Any],
        saved_file_info: Dict[str, Any]
    ) -> CodeReviewResult:
        """
        生成最终审查结果
        
        Args:
            file_content: 原始代码
            file_name: 文件名
            architect_result: 架构分析结果
            reviewer_result: 代码审查结果
            optimizer_result: 优化结果
            saved_file_info: 保存的文件信息
            
        Returns:
            审查结果
        """
        from app.utils.diff_utils import calculate_diff_stats
        
        # 计算差异统计
        fixed_code = optimizer_result.get("fixed_code", "")
        diff_stats = calculate_diff_stats(file_content, fixed_code)
        
        # 构建结果
        result = CodeReviewResult(
            id=self.task_id,
            file_name=file_name,
            original_content=file_content,
            fixed_content=fixed_code,
            architect_report=json.dumps(architect_result, ensure_ascii=False, indent=2),
            reviewer_report=json.dumps(reviewer_result, ensure_ascii=False, indent=2),
            optimizer_summary=optimizer_result.get("summary", ""),
            quality_score=optimizer_result.get("quality_score", 0.0),
            saved_file_path=saved_file_info.get("file_path", ""),
            diff_stats=diff_stats
        )
        
        return result
    
    async def _update_progress(
        self,
        step: AgentStep,
        progress: float,
        message: str
    ):
        """
        更新总体进度
        
        Args:
            step: 当前步骤
            progress: 进度百分比
            message: 进度消息
        """
        self.current_progress = AgentProgress(
            step=step,
            progress=progress,
            message=message
        )
        
        # 发送进度更新
        await self.ws_manager.broadcast_to_task(
            self.task_id,
            {
                "type": "progress_update",
                "data": {
                    "task_id": self.task_id,
                    "step": step.value,
                    "progress": progress,
                    "message": message
                }
            }
        )
    
    async def _notify_agent_status(
        self,
        agent_name: str,
        message: str,
        progress: Optional[float] = None
    ):
        """
        发送智能体状态通知
        
        Args:
            agent_name: 智能体名称
            message: 状态消息
            progress: 进度百分比
        """
        status_data = {
            "agent": agent_name,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if progress is not None:
            status_data["progress"] = progress
        
        await self.ws_manager.broadcast_to_task(
            self.task_id,
            {
                "type": "agent_update",
                "data": status_data
            }
        )