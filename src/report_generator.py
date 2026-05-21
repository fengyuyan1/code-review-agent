"""报告生成模块"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from reviewer import CodeReviewResult, ReviewIssue, ReviewSeverity


class ReportGenerator:
    """报告生成器"""

    def __init__(self, format: str = "markdown"):
        """初始化报告生成器

        Args:
            format: 报告格式 ("markdown", "json", "html")
        """
        self.format = format
        self.supported_formats = ["markdown", "json", "html"]

        if format not in self.supported_formats:
            raise ValueError(f"不支持的格式: {format}，支持: {self.supported_formats}")

    def generate_report(self, result: CodeReviewResult) -> str:
        """生成审查报告

        Args:
            result: 代码审查结果

        Returns:
            格式化的报告文本
        """
        if self.format == "markdown":
            return self._generate_markdown_report(result)
        elif self.format == "json":
            return self._generate_json_report(result)
        elif self.format == "html":
            return self._generate_html_report(result)

    def _generate_markdown_report(self, result: CodeReviewResult) -> str:
        """生成 Markdown 格式报告"""
        lines = []

        # 标题
        lines.append(f"# 代码审查报告\n")
        lines.append(f"**文件**: {result.file_name}\n")
        lines.append(f"**语言**: {result.language}\n")
        lines.append(f"**总行数**: {result.total_lines}\n")
        lines.append(f"**审查分数**: {result.score:.1f}/100\n")
        lines.append(f"**审查时间**: {result.review_time_ms}ms\n")
        lines.append(f"**生成时间**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 摘要
        lines.append(f"\n## 摘要\n")
        lines.append(f"{result.summary}\n")

        # 问题统计
        if result.issues:
            lines.append(f"\n## 问题统计\n")
            severity_counts = self._count_by_severity(result.issues)
            for severity, count in severity_counts.items():
                lines.append(f"- **{severity}**: {count} 个\n")

            # 按类别分组的问题
            lines.append(f"\n## 详细问题\n")
            issues_by_category = self._group_by_category(result.issues)

            for category, issues in issues_by_category.items():
                lines.append(f"\n### {category}\n")
                for i, issue in enumerate(issues, 1):
                    lines.append(f"\n#### 问题 {i}: {issue.title}\n")
                    lines.append(f"**严重程度**: {issue.severity.value}\n")
                    lines.append(f"**描述**: {issue.description}\n")

                    if issue.line_number:
                        lines.append(f"**行号**: {issue.line_number}\n")

                    if issue.suggestion:
                        lines.append(f"**建议**: {issue.suggestion}\n")

                    if issue.code_snippet:
                        lines.append(f"**代码片段**:\n")
                        lines.append(f"```\n{issue.code_snippet}\n```\n")
        else:
            lines.append(f"\n## 问题\n")
            lines.append(f"未发现问题。\n")

        return "".join(lines)

    def _generate_json_report(self, result: CodeReviewResult) -> str:
        """生成 JSON 格式报告"""
        report_dict = {
            "file_name": result.file_name,
            "language": result.language,
            "total_lines": result.total_lines,
            "score": result.score,
            "summary": result.summary,
            "review_time_ms": result.review_time_ms,
            "timestamp": result.timestamp.isoformat(),
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "title": issue.title,
                    "description": issue.description,
                    "line_number": issue.line_number,
                    "suggestion": issue.suggestion,
                    "code_snippet": issue.code_snippet,
                }
                for issue in result.issues
            ],
            "statistics": {
                "total_issues": len(result.issues),
                "by_severity": self._count_by_severity(result.issues),
                "by_category": self._count_by_category(result.issues),
            },
        }

        return json.dumps(report_dict, ensure_ascii=False, indent=2)

    def _generate_html_report(self, result: CodeReviewResult) -> str:
        """生成 HTML 格式报告"""
        severity_colors = {
            "信息": "#17a2b8",
            "警告": "#ffc107",
            "错误": "#dc3545",
            "严重": "#721c24",
        }

        html_parts = []

        # HTML 头部
        html_parts.append(
            """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码审查报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .info-item {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .info-item strong {
            display: block;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .info-item span {
            font-size: 1.2em;
            color: #2c3e50;
        }
        .score {
            font-size: 2em;
            font-weight: bold;
        }
        .score.excellent {
            color: #27ae60;
        }
        .score.good {
            color: #3498db;
        }
        .score.fair {
            color: #f39c12;
        }
        .score.poor {
            color: #e74c3c;
        }
        .statistics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-card .label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .issue {
            background-color: #f8f9fa;
            border-left: 4px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .issue.critical {
            border-left-color: #721c24;
            background-color: #f8d7da;
        }
        .issue.error {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }
        .issue.warning {
            border-left-color: #ffc107;
            background-color: #fff3cd;
        }
        .issue.info {
            border-left-color: #17a2b8;
            background-color: #d1ecf1;
        }
        .issue-title {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .issue-severity {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 10px;
        }
        .severity-critical {
            background-color: #721c24;
        }
        .severity-error {
            background-color: #dc3545;
        }
        .severity-warning {
            background-color: #ffc107;
            color: #333;
        }
        .severity-info {
            background-color: #17a2b8;
        }
        .issue-detail {
            margin: 8px 0;
            color: #555;
        }
        .issue-detail strong {
            color: #333;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
"""
        )

        # 标题和基本信息
        html_parts.append("<h1>代码审查报告</h1>\n")

        # 信息网格
        html_parts.append("<div class='info-grid'>\n")
        html_parts.append(f"<div class='info-item'><strong>文件</strong><span>{result.file_name}</span></div>\n")
        html_parts.append(f"<div class='info-item'><strong>语言</strong><span>{result.language}</span></div>\n")
        html_parts.append(f"<div class='info-item'><strong>总行数</strong><span>{result.total_lines}</span></div>\n")

        # 分数
        score_class = "excellent" if result.score >= 90 else "good" if result.score >= 70 else "fair" if result.score >= 50 else "poor"
        html_parts.append(
            f"<div class='info-item'><strong>审查分数</strong><span class='score {score_class}'>{result.score:.1f}/100</span></div>\n"
        )

        html_parts.append(f"<div class='info-item'><strong>审查时间</strong><span>{result.review_time_ms}ms</span></div>\n")
        html_parts.append(
            f"<div class='info-item'><strong>生成时间</strong><span>{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span></div>\n"
        )
        html_parts.append("</div>\n")

        # 摘要
        html_parts.append("<h2>摘要</h2>\n")
        html_parts.append(f"<p>{result.summary}</p>\n")

        # 问题统计
        if result.issues:
            html_parts.append("<h2>问题统计</h2>\n")
            html_parts.append("<div class='statistics'>\n")

            severity_counts = self._count_by_severity(result.issues)
            for severity, count in severity_counts.items():
                severity_key = severity.lower()
                html_parts.append(f"<div class='stat-card'>\n")
                html_parts.append(f"<div class='label'>{severity}</div>\n")
                html_parts.append(f"<div class='number'>{count}</div>\n")
                html_parts.append(f"</div>\n")

            html_parts.append("</div>\n")

            # 详细问题
            html_parts.append("<h2>详细问题</h2>\n")
            issues_by_category = self._group_by_category(result.issues)

            for category, issues in issues_by_category.items():
                html_parts.append(f"<h3>{category}</h3>\n")

                for issue in issues:
                    severity_key = issue.severity.value.lower()
                    severity_class = "critical" if issue.severity == ReviewSeverity.CRITICAL else "error" if issue.severity == ReviewSeverity.ERROR else "warning" if issue.severity == ReviewSeverity.WARNING else "info"

                    html_parts.append(f"<div class='issue {severity_class}'>\n")
                    html_parts.append(f"<div class='issue-title'>{issue.title}</div>\n")
                    html_parts.append(
                        f"<span class='issue-severity severity-{severity_key}'>{issue.severity.value}</span>\n"
                    )
                    html_parts.append(f"<div class='issue-detail'><strong>描述:</strong> {issue.description}</div>\n")

                    if issue.line_number:
                        html_parts.append(f"<div class='issue-detail'><strong>行号:</strong> {issue.line_number}</div>\n")

                    if issue.suggestion:
                        html_parts.append(f"<div class='issue-detail'><strong>建议:</strong> {issue.suggestion}</div>\n")

                    if issue.code_snippet:
                        html_parts.append(f"<div class='issue-detail'><strong>代码片段:</strong></div>\n")
                        html_parts.append(f"<pre><code>{issue.code_snippet}</code></pre>\n")

                    html_parts.append("</div>\n")
        else:
            html_parts.append("<h2>问题</h2>\n")
            html_parts.append("<p>未发现问题。</p>\n")

        # 页脚
        html_parts.append(
            f"<div class='footer'>报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>\n"
        )

        # HTML 结尾
        html_parts.append(
            """    </div>
</body>
</html>"""
        )

        return "".join(html_parts)

    def _count_by_severity(self, issues: List[ReviewIssue]) -> Dict[str, int]:
        """按严重程度统计问题"""
        counts = {
            "严重": 0,
            "错误": 0,
            "警告": 0,
            "信息": 0,
        }

        for issue in issues:
            counts[issue.severity.value] += 1

        return counts

    def _count_by_category(self, issues: List[ReviewIssue]) -> Dict[str, int]:
        """按类别统计问题"""
        counts = {}
        for issue in issues:
            counts[issue.category] = counts.get(issue.category, 0) + 1

        return counts

    def _group_by_category(self, issues: List[ReviewIssue]) -> Dict[str, List[ReviewIssue]]:
        """按类别分组问题"""
        grouped = {}
        for issue in issues:
            if issue.category not in grouped:
                grouped[issue.category] = []
            grouped[issue.category].append(issue)

        return grouped

    def generate_batch_report(self, results: List[CodeReviewResult]) -> str:
        """生成批量审查报告

        Args:
            results: 代码审查结果列表

        Returns:
            格式化的批量报告文本
        """
        if self.format == "markdown":
            return self._generate_batch_markdown_report(results)
        elif self.format == "json":
            return self._generate_batch_json_report(results)
        elif self.format == "html":
            return self._generate_batch_html_report(results)

    def _generate_batch_markdown_report(self, results: List[CodeReviewResult]) -> str:
        """生成批量 Markdown 报告"""
        lines = []

        lines.append("# 批量代码审查报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**审查文件数**: {len(results)}\n\n")

        # 统计摘要
        total_issues = sum(len(r.issues) for r in results)
        avg_score = sum(r.score for r in results) / len(results) if results else 0

        lines.append("## 统计摘要\n")
        lines.append(f"- **总问题数**: {total_issues}\n")
        lines.append(f"- **平均分数**: {avg_score:.1f}/100\n")
        lines.append(f"- **总审查时间**: {sum(r.review_time_ms for r in results)}ms\n\n")

        # 文件列表
        lines.append("## 审查文件\n\n")
        for i, result in enumerate(results, 1):
            lines.append(f"### {i}. {result.file_name}\n")
            lines.append(f"- **语言**: {result.language}\n")
            lines.append(f"- **分数**: {result.score:.1f}/100\n")
            lines.append(f"- **问题数**: {len(result.issues)}\n")
            lines.append(f"- **摘要**: {result.summary}\n\n")

        return "".join(lines)

    def _generate_batch_json_report(self, results: List[CodeReviewResult]) -> str:
        """生成批量 JSON 报告"""
        report_dict = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(results),
            "total_issues": sum(len(r.issues) for r in results),
            "average_score": sum(r.score for r in results) / len(results) if results else 0,
            "total_review_time_ms": sum(r.review_time_ms for r in results),
            "files": [
                {
                    "file_name": r.file_name,
                    "language": r.language,
                    "score": r.score,
                    "issues_count": len(r.issues),
                    "summary": r.summary,
                }
                for r in results
            ],
        }

        return json.dumps(report_dict, ensure_ascii=False, indent=2)

    def _generate_batch_html_report(self, results: List[CodeReviewResult]) -> str:
        """生成批量 HTML 报告"""
        html_parts = []

        html_parts.append(
            """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量代码审查报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .summary-item {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .summary-item strong {
            display: block;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .summary-item span {
            font-size: 1.5em;
            color: #2c3e50;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .score-excellent {
            color: #27ae60;
            font-weight: bold;
        }
        .score-good {
            color: #3498db;
            font-weight: bold;
        }
        .score-fair {
            color: #f39c12;
            font-weight: bold;
        }
        .score-poor {
            color: #e74c3c;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
"""
        )

        html_parts.append("<h1>批量代码审查报告</h1>\n")

        # 统计摘要
        total_issues = sum(len(r.issues) for r in results)
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        total_time = sum(r.review_time_ms for r in results)

        html_parts.append("<div class='summary-grid'>\n")
        html_parts.append(f"<div class='summary-item'><strong>审查文件数</strong><span>{len(results)}</span></div>\n")
        html_parts.append(f"<div class='summary-item'><strong>总问题数</strong><span>{total_issues}</span></div>\n")
        html_parts.append(f"<div class='summary-item'><strong>平均分数</strong><span>{avg_score:.1f}/100</span></div>\n")
        html_parts.append(f"<div class='summary-item'><strong>总审查时间</strong><span>{total_time}ms</span></div>\n")
        html_parts.append("</div>\n")

        # 文件表格
        html_parts.append("<h2>审查文件</h2>\n")
        html_parts.append("<table>\n")
        html_parts.append("<thead><tr><th>文件名</th><th>语言</th><th>分数</th><th>问题数</th><th>摘要</th></tr></thead>\n")
        html_parts.append("<tbody>\n")

        for result in results:
            score_class = "excellent" if result.score >= 90 else "good" if result.score >= 70 else "fair" if result.score >= 50 else "poor"
            html_parts.append(f"<tr>\n")
            html_parts.append(f"<td>{result.file_name}</td>\n")
            html_parts.append(f"<td>{result.language}</td>\n")
            html_parts.append(f"<td class='score-{score_class}'>{result.score:.1f}</td>\n")
            html_parts.append(f"<td>{len(result.issues)}</td>\n")
            html_parts.append(f"<td>{result.summary}</td>\n")
            html_parts.append(f"</tr>\n")

        html_parts.append("</tbody>\n")
        html_parts.append("</table>\n")

        # 页脚
        html_parts.append(
            f"<div class='footer'>报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>\n"
        )

        html_parts.append(
            """    </div>
</body>
</html>"""
        )

        return "".join(html_parts)
