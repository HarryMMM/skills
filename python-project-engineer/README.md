# Python 工程实施助手

标准化 Python 工程脚手架生成、重构与新特性开发技能，内置自动验证与人工复核清单。

## 功能

| 模式 | 说明 |
|---|---|
| `new` | 从零创建标准化 Python 工程脚手架 |
| `refactor` | 将现有 Python 项目重构为标准结构 |
| `feature` | 在现有工程中新增功能模块 |

## 工程标准

### 目录结构
```
app/
  main.py              # 应用入口
  api/                 # REST API 入口
  config/              # pydantic-settings 配置
  core/                # 日志 / 异常
  db/                  # SQLAlchemy async 连接管理
  models/              # 数据模型
  repositories/        # 数据访问层
  services/            # 业务逻辑层
  tools/               # MCP 工具 / 对外编排
  utils/               # 通用工具
tests/
```

### 分层约束
```
tools/api → services → repositories
```
- tools/api：禁止直接访问数据库
- services：禁止直接执行 SQL
- repositories：承担所有数据访问，SQL 必须参数化

### 技术栈
- 配置：`pydantic-settings`
- 日志：标准 `logging` + 彩色 Formatter
- 数据访问：`SQLAlchemy 2.x` async + `aiomysql`
- 格式化：`ruff`（行宽 100）

## 使用方式

在 Qoder CN 中调用技能，提供以下信息：

1. **项目名称**（必填）
2. **项目类型或一句话定位**（必填）
3. **工作模式**：`new` / `refactor` / `feature`（必填）

可选参数：
- Python 版本（默认 3.13）
- 包名（默认由项目名规范化）
- Docker / CI / 测试骨架（默认开启）

## 自动验证

每个流程结束后自动运行：
1. 结构检查 — 目录/文件存在性、禁止目录
2. 配置检查 — pyproject.toml / .env.example 关键配置
3. 分层/风格检查 — api/tools/services 分层约束、print 检测
4. 编译/导入冒烟检查

输出三段式报告：
- 自动验证通过
- 自动验证失败或受阻
- 需要人工确认

## 项目结构

```
python-project-engineer/
├── SKILL.md                          # 技能入口文档
├── agents/                           # 子流程
│   ├── new_project.md                # 新建工程流程
│   ├── refactor_project.md           # 重构工程流程
│   └── feature_development.md        # 新特性开发流程
├── assets/                           # 模板文件
│   ├── pyproject.toml.template       # 项目配置
│   ├── Dockerfile.template           # 容器构建
│   ├── .env.example.template         # 环境变量示例
│   ├── README.md.template            # 项目说明
│   ├── ci-github.yml.template        # GitHub Actions CI
│   ├── .gitignore.template           # Git 忽略规则
│   └── skeleton/                     # 骨架代码模板
│       └── app/
│           ├── main.py.template
│           ├── config/settings.py.template
│           ├── core/logging.py.template
│           ├── core/exceptions.py.template
│           ├── db/connection.py.template
│           └── repositories/base_repository.py.template
└── scripts/                          # 验证脚本
    ├── run_validation.py             # 编排脚本（入口）
    ├── check_structure.py            # 结构检查
    ├── check_config.py               # 配置检查
    ├── check_style_conventions.py    # 分层/风格检查
    └── smoke_check.py                # 编译/导入冒烟检查
```
# python-project-engineer
