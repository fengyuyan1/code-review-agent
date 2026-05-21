# Code Review Agent - AI 驱动的代码审查系统

## 项目概述

**Code Review Agent** 是一个基于 Claude AI 的智能代码审查系统，通过 AI Agent 工作流实现迭代式代码质量分析和优化建议。该项目展示了在实际应用中对 Claude API 的深度集成、Token 消耗管理和 AI 智能体的熟练使用。

### 核心特性

- **智能代码审查**：支持 Python、JavaScript、Java 等多种编程语言
- **多维度分析**：代码质量、性能优化、安全性、可维护性、最佳实践
- **迭代式优化**：AI Agent 通过多轮对话逐步优化审查结果
- **Token 追踪**：精细化的 Token 消耗统计和成本分析
- **多格式报告**：支持 Markdown、JSON、HTML 三种输出格式
- **对话管理**：完整的会话状态管理和历史记录导出

---

## 项目结构

```
code-review-agent/
├── config.py                          # 中央配置文件
├── requirements.txt                   # 依赖列表
├── README.md                          # 项目文档
├── .gitignore                         # Git 忽略规则
├── basic_review.py                    # 基本使用示例
├── src/
│   ├── __init__.py
│   ├── token_tracker.py              # Token 消耗追踪模块
│   ├── reviewer.py                   # 代码审查引擎
│   ├── agent.py                      # AI Agent 工作流编排
│   └── report_generator.py           # 报告生成模块
└── demo_data/
    └── sample_code/
        ├── python_quality_issues.py  # Python 示例代码
        ├── javascript_quality_issues.js  # JavaScript 示例代码
        └── java_quality_issues.java  # Java 示例代码
```

---

## 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone <repository-url>
cd code-review-agent

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. 基本使用

```python
from src.reviewer import CodeReviewer
from src.agent import CodeReviewAgent
from src.token_tracker import TokenTracker
from src.report_generator import ReportGenerator

# 初始化组件
reviewer = CodeReviewer()
token_tracker = TokenTracker()
agent = CodeReviewAgent(reviewer, token_tracker)

# 开始审查会话
session_id = "review_001"
agent.start_review_session(session_id)

# 审查代码
code = """
def process_user_data(users):
    result = ""
    for user in users:
        result += user['name'] + " - " + user['email'] + "\\n"
    return result
"""

result = agent.review_code_iteratively(
    code=code,
    file_name="example.py",
    language="python"
)

# 生成报告
report_gen = ReportGenerator()
report = report_gen.generate_report(result, format="markdown")
print(report)
```

### 3. 运行示例脚本

```bash
python basic_review.py
```

---

## 核心模块说明

### Token Tracker（Token 追踪）

**功能**：精细化的 Token 消耗统计和成本分析

```python
from src.token_tracker import TokenTracker

tracker = TokenTracker()
tracker.start_batch("batch_001")

# 记录 Token 使用
tracker.record_usage(
    input_tokens=100,
    output_tokens=50,
    model="claude-3-5-sonnet",
    operation="code_review"
)

# 获取统计信息
stats = tracker.get_batch_summary("batch_001")
print(f"总 Token 数: {stats.total_tokens}")
print(f"成本: ${stats.estimated_cost:.4f}")
```

**关键指标**：
- 单次操作 Token 消耗
- 批次级别统计
- 模型成本估算
- 操作类型分类

---

### Code Reviewer（代码审查引擎）

**功能**：多维度代码质量分析

```python
from src.reviewer import CodeReviewer, ReviewSeverity

reviewer = CodeReviewer()
result = reviewer.review_code(
    code=code_content,
    file_name="example.py",
    language="python"
)

# 审查结果包含
print(f"审查分数: {result.score}/100")
print(f"发现问题数: {len(result.issues)}")
print(f"审查耗时: {result.review_time_ms}ms")

# 问题分类
for issue in result.issues:
    print(f"[{issue.severity.value}] {issue.title}")
    print(f"  描述: {issue.description}")
    print(f"  建议: {issue.suggestion}")
```

**审查维度**：
- **代码质量**：行长度、空行、命名规范
- **性能优化**：嵌套循环、字符串拼接、算法复杂度
- **安全性**：eval()、exec()、命令注入、反序列化攻击
- **可维护性**：函数长度、注释比例、代码复杂度
- **最佳实践**：异常处理、资源管理、类型提示

**严重程度分类**：
- `INFO`：信息提示（1 分）
- `WARNING`：警告（5 分）
- `ERROR`：错误（15 分）
- `CRITICAL`：严重（30 分）

---

### Code Review Agent（AI 智能体）

**功能**：迭代式代码审查优化

```python
from src.agent import CodeReviewAgent, AgentState

agent = CodeReviewAgent(
    reviewer=reviewer,
    token_tracker=token_tracker,
    max_iterations=5,
    temperature=0.7
)

# 开始会话
session_id = "review_session_001"
agent.start_review_session(session_id)

# 迭代式审查
result = agent.review_code_iteratively(
    code=code_content,
    file_name="example.py",
    language="python",
    context={"project": "my_project"}
)

# 获取对话摘要
summary = agent.get_conversation_summary(session_id)
print(f"迭代次数: {summary['iterations']}")
print(f"消耗 Token: {summary['total_tokens']}")
print(f"对话消息数: {summary['message_count']}")

# 导出完整对话记录
conversation = agent.export_conversation(session_id)
```

**工作流**：
1. **初始审查**：执行全面的代码审查
2. **问题识别**：提取严重问题
3. **迭代优化**：基于严重问题生成优化建议
4. **状态管理**：追踪 Agent 状态（IDLE → ANALYZING → REFINING → COMPLETED）
5. **对话记录**：保存完整的 AI 对话历史

---

### Report Generator（报告生成）

**功能**：多格式报告输出

```python
from src.report_generator import ReportGenerator

report_gen = ReportGenerator()

# Markdown 格式
markdown_report = report_gen.generate_report(result, format="markdown")

# JSON 格式
json_report = report_gen.generate_report(result, format="json")

# HTML 格式
html_report = report_gen.generate_report(result, format="html")

# 批量报告
batch_report = report_gen.generate_batch_report(
    results=[result1, result2, result3],
    format="markdown"
)
```

**输出格式**：
- **Markdown**：易于阅读和分享
- **JSON**：便于程序化处理
- **HTML**：可视化展示

---

## Token 消耗分析

### 单次审查 Token 消耗估算

| 操作 | 输入 Token | 输出 Token | 总计 |
|------|-----------|----------|------|
| 初始审查 | 200-500 | 100-300 | 300-800 |
| 迭代优化（单次） | 150-300 | 100-200 | 250-500 |
| 报告生成 | 50-100 | 50-150 | 100-250 |

### 批量审查 Token 消耗

- **10 个文件审查**：3,000-8,000 Token
- **100 个文件审查**：30,000-80,000 Token
- **1,000 个文件审查**：300,000-800,000 Token

### 成本估算（基于 Claude 3.5 Sonnet）

- 输入：$3 / 1M tokens
- 输出：$15 / 1M tokens

**示例**：
- 单个文件审查：$0.003-0.012
- 100 个文件审查：$0.09-0.12
- 1,000 个文件审查：$0.9-1.2

---

## 配置说明

编辑 `config.py` 自定义项目行为：

```python
# Claude API 配置
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
CLAUDE_API_KEY = "your-api-key"  # 从环境变量读取

# Token 限制
MAX_TOKENS_PER_REQUEST = 4096
MAX_TOKENS_PER_BATCH = 100000

# Agent 工作流配置
MAX_ITERATIONS = 5
TEMPERATURE = 0.7

# 审查重点领域
FOCUS_AREAS = [
    "代码质量",
    "性能优化",
    "安全性",
    "可维护性",
    "最佳实践"
]

# 演示数据路径
DEMO_DATA_PATH = "demo_data/sample_code"

# 报告输出配置
REPORT_OUTPUT_DIR = "reports"
REPORT_FORMATS = ["markdown", "json", "html"]
```

---

## 使用场景

### 场景 1：代码质量把关

```python
# 在 CI/CD 流程中集成代码审查
reviewer = CodeReviewer()
result = reviewer.review_code(code, "main.py", "python")

if result.score < 70:
    print("代码质量不达标，请修复问题后重新提交")
    exit(1)
```

### 场景 2：团队代码审查

```python
# 为团队成员的代码提供自动审查建议
agent = CodeReviewAgent(reviewer, token_tracker)
agent.start_review_session("team_review_001")

for file_path in code_files:
    with open(file_path) as f:
        code = f.read()
    
    result = agent.review_code_iteratively(
        code=code,
        file_name=file_path,
        language="python"
    )
    
    # 生成报告
    report = report_gen.generate_report(result, format="markdown")
    print(report)
```

### 场景 3：成本分析

```python
# 分析代码审查的 Token 消耗和成本
token_tracker.start_batch("cost_analysis")

# 执行审查...

stats = token_tracker.get_batch_summary("cost_analysis")
print(f"总 Token: {stats.total_tokens}")
print(f"预估成本: ${stats.estimated_cost:.4f}")
```

---

## 示例代码

项目包含三个演示代码文件，展示各种代码质量问题：

### Python 示例（`demo_data/sample_code/python_quality_issues.py`）

- 连续空行过多
- 低效的字符串拼接
- 深层嵌套循环
- eval() 安全风险
- 过于宽泛的异常处理
- 超长行

### JavaScript 示例（`demo_data/sample_code/javascript_quality_issues.js`）

- 使用 var 而不是 const/let
- 回调地狱
- 全局变量污染
- 没有错误处理的异步操作
- 使用 eval()
- 嵌套过深

### Java 示例（`demo_data/sample_code/java_quality_issues.java`）

- 使用原始类型而不是泛型
- 过度使用 synchronized
- 忽略异常
- 嵌套循环性能问题
- 滥用反射
- 没有资源管理

---

## 依赖项

- **anthropic**：Claude API 客户端
- **python-dotenv**：环境变量管理
- **dataclasses**：数据结构定义（Python 3.7+）

详见 `requirements.txt`

---

## 项目亮点

### 1. 深度 Claude API 集成

- 完整的 API 调用流程
- 精细化的 Token 消耗追踪
- 成本估算和优化

### 2. AI 智能体工作流

- 多轮对话管理
- 自适应迭代策略
- 状态机设计
- 对话历史导出

### 3. 生产级代码质量

- 类型提示和数据类
- 模块化架构
- 可扩展的审查规则
- 多格式报告生成

### 4. 实用的演示数据

- 真实的代码质量问题
- 多语言支持
- 完整的问题分类

---

## 扩展方向

1. **集成更多编程语言**：Go、Rust、TypeScript 等
2. **自定义审查规则**：支持用户定义的检查规则
3. **Web 界面**：提供可视化的审查结果展示
4. **IDE 插件**：集成到 VS Code、JetBrains 等编辑器
5. **团队协作**：支持多用户、权限管理、审查流程
6. **性能优化**：批量审查、缓存、并行处理

---

## 许可证

MIT License

---


