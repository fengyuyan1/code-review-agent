"""AI Agent 工作流模块"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from reviewer import CodeReviewer, CodeReviewResult, ReviewIssue
from token_tracker import TokenTracker, TokenUsage


class AgentState(Enum):
    """Agent 状态"""
    IDLE = "空闲"
    ANALYZING = "分析中"
    REFINING = "优化中"
    COMPLETED = "已完成"
    FAILED = "失败"


@dataclass
class AgentMessage:
    """Agent 消息"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime = None
    tokens_used: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentConversation:
    """Agent 对话记录"""
    conversation_id: str
    messages: List[AgentMessage]
    state: AgentState
    iterations: int = 0
    total_tokens: int = 0
    start_time: datetime = None
    end_time: datetime = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()


class CodeReviewAgent:
    """代码审查 AI Agent"""

    def __init__(
        self,
        reviewer: CodeReviewer,
        token_tracker: TokenTracker,
        max_iterations: int = 5,
        temperature: float = 0.7
    ):
        """初始化 Agent

        Args:
            reviewer: 代码审查引擎
            token_tracker: Token 追踪器
            max_iterations: 最大迭代次数
            temperature: 模型温度参数
        """
        self.reviewer = reviewer
        self.token_tracker = token_tracker
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.conversations: Dict[str, AgentConversation] = {}
        self.current_conversation_id: str = ""

    def start_review_session(self, session_id: str) -> str:
        """开始审查会话

        Args:
            session_id: 会话 ID

        Returns:
            会话 ID
        """
        self.current_conversation_id = session_id
        self.token_tracker.start_batch(session_id)

        conversation = AgentConversation(
            conversation_id=session_id,
            messages=[],
            state=AgentState.IDLE
        )
        self.conversations[session_id] = conversation
        return session_id

    def add_message(
        self,
        role: str,
        content: str,
        tokens_used: int = 0
    ) -> AgentMessage:
        """添加消息到当前对话

        Args:
            role: 角色 ("user" 或 "assistant")
            content: 消息内容
            tokens_used: 使用的 Token 数

        Returns:
            添加的消息
        """
        if self.current_conversation_id not in self.conversations:
            raise ValueError(f"会话 {self.current_conversation_id} 不存在")

        message = AgentMessage(
            role=role,
            content=content,
            tokens_used=tokens_used
        )

        conversation = self.conversations[self.current_conversation_id]
        conversation.messages.append(message)
        conversation.total_tokens += tokens_used

        if tokens_used > 0:
            self.token_tracker.record_usage(
                input_tokens=tokens_used // 2,
                output_tokens=tokens_used // 2,
                model="claude-3-5-sonnet",
                operation="review_iteration"
            )

        return message

    def review_code_iteratively(
        self,
        code: str,
        file_name: str,
        language: str,
        context: Optional[Dict] = None
    ) -> CodeReviewResult:
        """迭代式审查代码

        Args:
            code: 代码内容
            file_name: 文件名
            language: 编程语言
            context: 额外上下文

        Returns:
            最终审查结果
        """
        conversation = self.conversations.get(self.current_conversation_id)
        if not conversation:
            raise ValueError(f"会话 {self.current_conversation_id} 不存在")

        conversation.state = AgentState.ANALYZING

        # 初始审查
        initial_review = self.reviewer.review_code(
            code=code,
            file_name=file_name,
            language=language,
            context=context
        )

        self.add_message(
            role="assistant",
            content=f"初始审查完成：{initial_review.summary}",
            tokens_used=500
        )

        current_result = initial_review
        conversation.iterations = 1

        # 迭代优化
        for iteration in range(1, self.max_iterations):
            if not current_result.issues or current_result.score >= 90:
                break

            conversation.state = AgentState.REFINING

            # 生成优化建议
            critical_issues = [
                i for i in current_result.issues
                if i.severity.value == "严重"
            ]

            if critical_issues:
                suggestion = self._generate_refinement_suggestion(
                    current_result,
                    critical_issues
                )

                self.add_message(
                    role="user",
                    content=suggestion,
                    tokens_used=300
                )

                self.add_message(
                    role="assistant",
                    content=f"迭代 {iteration}: 已分析关键问题，建议修复优先级",
                    tokens_used=400
                )

            conversation.iterations = iteration + 1

        conversation.state = AgentState.COMPLETED
        conversation.end_time = datetime.now()

        return current_result

    def _generate_refinement_suggestion(
        self,
        result: CodeReviewResult,
        critical_issues: List[ReviewIssue]
    ) -> str:
        """生成优化建议

        Args:
            result: 审查结果
            critical_issues: 严重问题列表

        Returns:
            优化建议文本
        """
        suggestions = []
        for issue in critical_issues[:3]:
            suggestions.append(
                f"- {issue.title}: {issue.suggestion}"
            )

        return "请关注以下严重问题：\n" + "\n".join(suggestions)

    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """获取对话摘要

        Args:
            conversation_id: 对话 ID

        Returns:
            对话摘要
        """
        if conversation_id not in self.conversations:
            return None

        conversation = self.conversations[conversation_id]
        duration = 0
        if conversation.end_time and conversation.start_time:
            duration = (
                conversation.end_time - conversation.start_time
            ).total_seconds()

        return {
            "conversation_id": conversation_id,
            "state": conversation.state.value,
            "iterations": conversation.iterations,
            "total_tokens": conversation.total_tokens,
            "message_count": len(conversation.messages),
            "duration_seconds": duration,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "tokens": msg.tokens_used
                }
                for msg in conversation.messages
            ]
        }

    def get_all_conversations(self) -> Dict[str, Dict]:
        """获取所有对话摘要

        Returns:
            所有对话摘要
        """
        return {
            cid: self.get_conversation_summary(cid)
            for cid in self.conversations.keys()
        }

    def export_conversation(self, conversation_id: str) -> Dict:
        """导出对话记录

        Args:
            conversation_id: 对话 ID

        Returns:
            完整对话记录
        """
        if conversation_id not in self.conversations:
            return None

        conversation = self.conversations[conversation_id]
        return {
            "conversation_id": conversation_id,
            "state": conversation.state.value,
            "iterations": conversation.iterations,
            "total_tokens": conversation.total_tokens,
            "start_time": conversation.start_time.isoformat(),
            "end_time": conversation.end_time.isoformat() if conversation.end_time else None,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "tokens_used": msg.tokens_used
                }
                for msg in conversation.messages
            ]
        }
