"""项目配置文件"""

# Claude API 配置
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
CLAUDE_API_KEY = "your-api-key-here"  # 用户需要自己填入

# Token 相关配置
TOKEN_LIMIT_PER_REQUEST = 4000
TOKEN_LIMIT_PER_BATCH = 10000

# 代码审查配置
REVIEW_FOCUS_AREAS = [
    "代码质量",
    "性能优化",
    "安全性",
    "可维护性",
    "最佳实践"
]

# Agent 工作流配置
AGENT_MAX_ITERATIONS = 5
AGENT_TEMPERATURE = 0.7

# 演示数据配置
DEMO_DATA_DIR = "demo_data"
SAMPLE_CODE_DIR = "demo_data/sample_code"

# 报告配置
REPORT_OUTPUT_DIR = "reports"
REPORT_FORMAT = "markdown"  # 支持: markdown, json, html
