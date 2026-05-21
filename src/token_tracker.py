"""Token 消耗追踪模块"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class TokenUsage:
    """单次 API 调用的 Token 使用情况"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    model: str = ""
    operation: str = ""


@dataclass
class BatchTokenStats:
    """批次 Token 统计"""
    batch_id: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0
    operations: Dict[str, int] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)


class TokenTracker:
    """Token 消耗追踪器"""

    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self.batch_stats: Dict[str, BatchTokenStats] = {}
        self.current_batch_id: str = ""

    def start_batch(self, batch_id: str) -> None:
        """开始新的批次追踪"""
        self.current_batch_id = batch_id
        self.batch_stats[batch_id] = BatchTokenStats(batch_id=batch_id)

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "",
        operation: str = ""
    ) -> TokenUsage:
        """记录单次 API 调用的 Token 使用"""
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model,
            operation=operation
        )
        self.usage_history.append(usage)

        # 更新当前批次统计
        if self.current_batch_id in self.batch_stats:
            batch = self.batch_stats[self.current_batch_id]
            batch.total_input_tokens += input_tokens
            batch.total_output_tokens += output_tokens
            batch.total_tokens += usage.total_tokens
            batch.call_count += 1
            batch.operations[operation] = batch.operations.get(operation, 0) + 1
            batch.end_time = datetime.now()

        return usage

    def end_batch(self) -> BatchTokenStats:
        """结束当前批次追踪"""
        if self.current_batch_id in self.batch_stats:
            batch = self.batch_stats[self.current_batch_id]
            batch.end_time = datetime.now()
            return batch
        return None

    def get_total_usage(self) -> Dict:
        """获取总体 Token 使用统计"""
        total_input = sum(u.input_tokens for u in self.usage_history)
        total_output = sum(u.output_tokens for u in self.usage_history)
        total = sum(u.total_tokens for u in self.usage_history)

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total,
            "call_count": len(self.usage_history),
            "average_tokens_per_call": total / len(self.usage_history) if self.usage_history else 0
        }

    def get_batch_summary(self, batch_id: str) -> Dict:
        """获取指定批次的摘要"""
        if batch_id not in self.batch_stats:
            return None

        batch = self.batch_stats[batch_id]
        duration = (batch.end_time - batch.start_time).total_seconds()

        return {
            "batch_id": batch_id,
            "total_tokens": batch.total_tokens,
            "input_tokens": batch.total_input_tokens,
            "output_tokens": batch.total_output_tokens,
            "call_count": batch.call_count,
            "average_tokens_per_call": batch.total_tokens / batch.call_count if batch.call_count > 0 else 0,
            "operations": batch.operations,
            "duration_seconds": duration
        }

    def get_operation_stats(self) -> Dict[str, Dict]:
        """按操作类型统计 Token 使用"""
        stats = {}
        for usage in self.usage_history:
            op = usage.operation or "unknown"
            if op not in stats:
                stats[op] = {
                    "count": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                }
            stats[op]["count"] += 1
            stats[op]["input_tokens"] += usage.input_tokens
            stats[op]["output_tokens"] += usage.output_tokens
            stats[op]["total_tokens"] += usage.total_tokens

        return stats

    def export_report(self) -> Dict:
        """导出完整的 Token 使用报告"""
        return {
            "total_usage": self.get_total_usage(),
            "operation_stats": self.get_operation_stats(),
            "batch_summaries": {
                bid: self.get_batch_summary(bid)
                for bid in self.batch_stats.keys()
            },
            "timestamp": datetime.now().isoformat()
        }
