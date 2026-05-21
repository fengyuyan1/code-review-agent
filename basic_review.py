"""基本使用示例 - 代码审查工作流演示"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.reviewer import CodeReviewer
from src.agent import CodeReviewAgent
from src.token_tracker import TokenTracker
from src.report_generator import ReportGenerator


def main():
    """演示代码审查工作流"""

    # 示例代码 - 包含多个质量问题
    sample_code = '''
def process_user_data(users):
    result = ""
    for user in users:
        result += user['name'] + " - " + user['email'] + "\\n"
    return result

def calculate_total(items):
    total = 0
    for item in items:
        for sub_item in item['values']:
            for value in sub_item:
                total += value
    return total

def validate_input(data):
    try:
        result = eval(data)
        return result
    except:
        return None
'''

    print("=" * 60)
    print("代码审查 Agent 演示")
    print("=" * 60)

    # 初始化组件
    print("\n[1] 初始化组件...")
    reviewer = CodeReviewer()
    token_tracker = TokenTracker()
    agent = CodeReviewAgent(reviewer, token_tracker, max_iterations=3)
    report_gen = ReportGenerator()

    # 开始审查会话
    print("[2] 开始审查会话...")
    session_id = "demo_review_001"
    agent.start_review_session(session_id)

    # 执行迭代式审查
    print("[3] 执行迭代式代码审查...")
    result = agent.review_code_iteratively(
        code=sample_code,
        file_name="example.py",
        language="python",
        context={"project": "demo_project"}
    )

    # 显示审查结果
    print("\n" + "=" * 60)
    print("审查结果")
    print("=" * 60)
    print(f"文件: {result.file_name}")
    print(f"语言: {result.language}")
    print(f"总行数: {result.total_lines}")
    print(f"审查分数: {result.score}/100")
    print(f"发现问题数: {len(result.issues)}")
    print(f"审查耗时: {result.review_time_ms}ms")
    print(f"\n摘要: {result.summary}")

    # 显示问题详情
    if result.issues:
        print("\n" + "-" * 60)
        print("问题详情")
        print("-" * 60)
        for i, issue in enumerate(result.issues[:5], 1):
            print(f"\n{i}. [{issue.severity.value}] {issue.title}")
            print(f"   类别: {issue.category}")
            print(f"   描述: {issue.description}")
            print(f"   建议: {issue.suggestion}")

    # 获取对话摘要
    print("\n" + "=" * 60)
    print("Agent 对话摘要")
    print("=" * 60)
    summary = agent.get_conversation_summary(session_id)
    print(f"会话 ID: {summary['conversation_id']}")
    print(f"Agent 状态: {summary['state']}")
    print(f"迭代次数: {summary['iterations']}")
    print(f"消息数: {summary['message_count']}")
    print(f"消耗 Token: {summary['total_tokens']}")
    print(f"耗时: {summary['duration_seconds']:.2f}s")

    # 获取 Token 统计
    print("\n" + "=" * 60)
    print("Token 消耗统计")
    print("=" * 60)
    batch_stats = token_tracker.get_batch_summary(session_id)
    if batch_stats:
        print(f"批次 ID: {batch_stats.batch_id}")
        print(f"总 Token: {batch_stats.total_tokens}")
        print(f"预估成本: ${batch_stats.estimated_cost:.4f}")
        print(f"操作数: {batch_stats.operations_count}")

    # 生成 Markdown 报告
    print("\n" + "=" * 60)
    print("生成 Markdown 报告")
    print("=" * 60)
    markdown_report = report_gen.generate_report(result, format="markdown")
    print(markdown_report[:500] + "...\n")

    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
