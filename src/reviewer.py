"""代码审查引擎模块"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ReviewSeverity(Enum):
    """审查问题严重程度"""
    INFO = "信息"
    WARNING = "警告"
    ERROR = "错误"
    CRITICAL = "严重"


@dataclass
class ReviewIssue:
    """单个审查问题"""
    severity: ReviewSeverity
    category: str
    title: str
    description: str
    line_number: Optional[int] = None
    suggestion: str = ""
    code_snippet: str = ""


@dataclass
class CodeReviewResult:
    """代码审查结果"""
    file_name: str
    language: str
    total_lines: int
    issues: List[ReviewIssue] = field(default_factory=list)
    summary: str = ""
    score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    review_time_ms: int = 0


class CodeReviewer:
    """代码审查引擎"""

    FOCUS_AREAS = [
        "代码质量",
        "性能优化",
        "安全性",
        "可维护性",
        "最佳实践"
    ]

    def __init__(self, focus_areas: Optional[List[str]] = None):
        """初始化审查引擎

        Args:
            focus_areas: 审查重点领域列表
        """
        self.focus_areas = focus_areas or self.FOCUS_AREAS
        self.review_history: List[CodeReviewResult] = []

    def review_code(
        self,
        code: str,
        file_name: str,
        language: str,
        context: Optional[Dict] = None
    ) -> CodeReviewResult:
        """审查代码

        Args:
            code: 代码内容
            file_name: 文件名
            language: 编程语言
            context: 额外上下文信息

        Returns:
            审查结果
        """
        import time
        start_time = time.time()

        result = CodeReviewResult(
            file_name=file_name,
            language=language,
            total_lines=len(code.split('\n'))
        )

        # 执行各类型审查
        self._check_code_quality(code, result)
        self._check_performance(code, result)
        self._check_security(code, result)
        self._check_maintainability(code, result)
        self._check_best_practices(code, result)

        # 计算审查分数
        result.score = self._calculate_score(result)
        result.summary = self._generate_summary(result)
        result.review_time_ms = int((time.time() - start_time) * 1000)

        self.review_history.append(result)
        return result

    def _check_code_quality(self, code: str, result: CodeReviewResult) -> None:
        """检查代码质量"""
        lines = code.split('\n')

        # 检查长行
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category="代码质量",
                    title="行过长",
                    description=f"第 {i} 行超过 120 个字符",
                    line_number=i,
                    suggestion="将长行分解为多行以提高可读性"
                ))

        # 检查空行过多
        consecutive_empty = 0
        for i, line in enumerate(lines, 1):
            if line.strip() == "":
                consecutive_empty += 1
                if consecutive_empty > 2:
                    result.issues.append(ReviewIssue(
                        severity=ReviewSeverity.INFO,
                        category="代码质量",
                        title="连续空行过多",
                        description=f"第 {i} 行附近有超过 2 个连续空行",
                        line_number=i,
                        suggestion="删除多余的空行"
                    ))
                    consecutive_empty = 0
            else:
                consecutive_empty = 0

    def _check_performance(self, code: str, result: CodeReviewResult) -> None:
        """检查性能问题"""
        # 检查嵌套循环
        if "for" in code and code.count("for") > 2:
            result.issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category="性能优化",
                title="可能存在嵌套循环",
                description="代码中包含多个循环，可能存在性能问题",
                suggestion="考虑使用更高效的算法或数据结构"
            ))

        # 检查字符串拼接
        if "+=" in code and "str" in code.lower():
            result.issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category="性能优化",
                title="字符串拼接效率低",
                description="使用 += 进行字符串拼接可能导致性能问题",
                suggestion="使用 join() 或 f-string 进行字符串操作"
            ))

    def _check_security(self, code: str, result: CodeReviewResult) -> None:
        """检查安全性问题"""
        security_patterns = [
            ("eval(", "使用 eval() 存在安全风险"),
            ("exec(", "使用 exec() 存在安全风险"),
            ("pickle", "pickle 模块可能存在反序列化攻击风险"),
            ("os.system(", "使用 os.system() 可能存在命令注入风险"),
            ("subprocess.call(shell=True", "shell=True 存在命令注入风险"),
        ]

        for pattern, message in security_patterns:
            if pattern in code:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.CRITICAL,
                    category="安全性",
                    title="安全风险",
                    description=message,
                    suggestion="使用更安全的替代方案"
                ))

    def _check_maintainability(self, code: str, result: CodeReviewResult) -> None:
        """检查可维护性"""
        lines = code.split('\n')

        # 检查函数长度
        current_function_lines = 0
        for line in lines:
            if line.strip().startswith("def ") or line.strip().startswith("function "):
                if current_function_lines > 50:
                    result.issues.append(ReviewIssue(
                        severity=ReviewSeverity.WARNING,
                        category="可维护性",
                        title="函数过长",
                        description="函数超过 50 行，难以维护",
                        suggestion="将函数分解为更小的单元"
                    ))
                current_function_lines = 0
            else:
                current_function_lines += 1

        # 检查注释
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        if comment_lines < len(lines) * 0.1:
            result.issues.append(ReviewIssue(
                severity=ReviewSeverity.INFO,
                category="可维护性",
                title="注释不足",
                description="代码注释比例低于 10%",
                suggestion="添加更多注释以提高代码可理解性"
            ))

    def _check_best_practices(self, code: str, result: CodeReviewResult) -> None:
        """检查最佳实践"""
        # 检查命名规范
        if "_" in code and not any(x in code for x in ["__init__", "__main__"]):
            # Python 风格检查
            if "def " in code:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.INFO,
                    category="最佳实践",
                    title="命名规范",
                    description="建议遵循 PEP 8 命名规范",
                    suggestion="使用 snake_case 命名函数和变量"
                ))

        # 检查异常处理
        if "try:" in code and "except:" in code:
            if "except:" in code and "except Exception" not in code:
                result.issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category="最佳实践",
                    title="异常处理过于宽泛",
                    description="使用裸 except 会捕获所有异常",
                    suggestion="指定具体的异常类型"
                ))

    def _calculate_score(self, result: CodeReviewResult) -> float:
        """计算审查分数 (0-100)"""
        if not result.issues:
            return 100.0

        severity_weights = {
            ReviewSeverity.INFO: 1,
            ReviewSeverity.WARNING: 5,
            ReviewSeverity.ERROR: 15,
            ReviewSeverity.CRITICAL: 30
        }

        total_deduction = sum(
            severity_weights.get(issue.severity, 0)
            for issue in result.issues
        )

        score = max(0, 100 - total_deduction)
        return score

    def _generate_summary(self, result: CodeReviewResult) -> str:
        """生成审查摘要"""
        if not result.issues:
            return "代码质量优秀，未发现问题。"

        critical_count = sum(1 for i in result.issues if i.severity == ReviewSeverity.CRITICAL)
        error_count = sum(1 for i in result.issues if i.severity == ReviewSeverity.ERROR)
        warning_count = sum(1 for i in result.issues if i.severity == ReviewSeverity.WARNING)
        info_count = sum(1 for i in result.issues if i.severity == ReviewSeverity.INFO)

        parts = []
        if critical_count > 0:
            parts.append(f"发现 {critical_count} 个严重问题")
        if error_count > 0:
            parts.append(f"{error_count} 个错误")
        if warning_count > 0:
            parts.append(f"{warning_count} 个警告")
        if info_count > 0:
            parts.append(f"{info_count} 个信息")

        return "，".join(parts) + "。"

    def get_review_statistics(self) -> Dict:
        """获取审查统计信息"""
        if not self.review_history:
            return {}

        total_issues = sum(len(r.issues) for r in self.review_history)
        avg_score = sum(r.score for r in self.review_history) / len(self.review_history)

        severity_counts = {
            "严重": sum(1 for r in self.review_history for i in r.issues if i.severity == ReviewSeverity.CRITICAL),
            "错误": sum(1 for r in self.review_history for i in r.issues if i.severity == ReviewSeverity.ERROR),
            "警告": sum(1 for r in self.review_history for i in r.issues if i.severity == ReviewSeverity.WARNING),
            "信息": sum(1 for r in self.review_history for i in r.issues if i.severity == ReviewSeverity.INFO),
        }

        return {
            "total_reviews": len(self.review_history),
            "total_issues": total_issues,
            "average_score": avg_score,
            "severity_distribution": severity_counts
        }
