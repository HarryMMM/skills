---
name: python-project-engineer
description: "当用户要创建标准化 Python 工程、重构现有 Python 项目结构、或在现有工程中新增功能模块时使用。支持自动验证与人工复核清单输出。"
argument-hint: "输入项目名、项目类型，以及 new/refactor/feature 模式"
user-invocable: true
---

# Python 工程实施助手

## 技能目标
1. 新建标准化 Python 工程脚手架
2. 重构现有 Python 工程为标准结构
3. 开发并集成新特性
4. 自动验证工程合规与可运行性

## 子流程路由
- [新建工程流程](./agents/new_project.md)
- [重构工程流程](./agents/refactor_project.md)
- [新特性开发流程](./agents/feature_development.md)

## 输入要求

### 必填
1. 项目名称
2. 项目类型或一句话定位
3. 工作模式：`new`、`refactor` 或 `feature`

### 可选（默认值）
- Python 版本：默认 `3.13`
- 包名/模块名：默认由项目名规范化
- 数据库模板：默认开启（单库）
- Docker：默认开启
- 测试骨架：默认开启
- 重构严格度：默认 `compatible`

## 工程标准

### 目录结构与职责
```text
app/
  __init__.py
  main.py              # 应用入口
  api/
    __init__.py        # REST API 入口
  config/
    __init__.py
    settings.py        # pydantic-settings 配置定义
  core/
    __init__.py
    logging.py         # logging 日志初始化
    exceptions.py      # 自定义异常
  db/
    __init__.py
    connection.py      # SQLAlchemy 引擎/会话
  models/
    __init__.py        # 数据模型定义
  repositories/
    __init__.py
    base_repository.py # 数据访问层基类
  services/
    __init__.py        # 业务逻辑层
  tools/
    __init__.py        # 对外调用入口（编排层）
  utils/
    __init__.py        # 通用工具函数
tests/
```

禁止目录：`evaluation/`、`pdm/`

### 分层约束
```
tools/api（编排入口）→ services（业务逻辑）→ repositories（数据访问）
```
- tools：MCP 工具，仅做对外编排，**禁止直接访问数据库**
- api：REST API，仅做对外编排，**禁止直接访问数据库**
- services：实现业务逻辑，**禁止直接执行 SQL**
- repositories：承担所有数据库访问，SQL **必须参数化**

### 技术栈与约束
| 领域 | 选型 | 备注 |
|---|---|---|
| 配置 | `pydantic-settings` | 配置外置，提供 `.env.example`，禁止硬编码密钥 |
| 日志 | 标准 `logging` + 彩色 Formatter | 禁止运行时 `print` |
| 数据访问 | `SQLAlchemy 2.x` async | 参数化 SQL，禁止拼接 |
| 异常 | 显式抛出 | 禁止吞异常、禁止静默失败 |
| 代码完整性 | 禁止 TODO/占位 | 所有实现必须完整可运行 |
| MCP | `mcp` SDK (FastMCP) | stdio 传输，自动注册 tools |
| 格式化 | `ruff` | 行宽 100 |

### 建议最小配置项
```env
DEBUG=false
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=app_db
```

### 依赖基线
- 核心：`pydantic`、`pydantic-settings`、`SQLAlchemy[asyncio]`、`aiomysql`、`mcp`
- 测试：`pytest`、`pytest-asyncio`
- 版本策略：稳定兼容优先，Python 默认 3.13

## 执行流程

### new：新建工程
1. 收集必填信息，应用默认值
2. **向用户展示收集到的信息，等待用户确认无误后继续**
3. 创建标准目录结构
4. 从 [assets](./assets/) 生成模板文件（替换占位变量）
5. 生成基础骨架代码
6. 执行验证流程
7. 输出结果与人工复核清单

### refactor：重构工程
1. 扫描现有目录与关键文件
2. 对照标准识别差异
3. **向用户展示扫描结果与差异清单，等待用户确认无误后继续**
4. 按"结构 → 基础设施 → 分层代码"顺序改造
5. 保持行为兼容，避免无关重构
6. 执行验证流程
7. 输出改造摘要、兼容说明与复核清单

### feature：新特性开发
1. 明确特性目标、输入输出与边界条件
2. **向用户展示需求分析结果，等待用户确认无误后继续**
3. 识别影响范围与落点文件（tool/service/repository）
4. 按分层约束实现功能
5. 补充必要测试或最小验证样例
6. 执行验证流程
7. 输出功能变更摘要、风险点与复核清单

## 自动验证

完成 new/refactor/feature 后，运行编排脚本：
```bash
python scripts/run_validation.py <project_root>
```

该脚本按顺序执行：结构检查 → 配置检查 → 分层/风格检查 → 编译/导入冒烟检查，并汇总输出。

验证输出固定三段：
1. **自动验证通过** — 列出通过的检查项
2. **自动验证失败或受阻** — 列出失败项及原因
3. **需要人工确认** — 列出自动化无法确认的事项

## 人工复核清单规则
仅输出自动化无法确认的事项：
- 环境变量真实值
- 外部数据库连通性
- 容器在目标环境启动
- 外部接口联调

## 资产文件

### 配置模板
| 文件 | 用途 |
|---|---|
| [pyproject.toml.template](./assets/pyproject.toml.template) | 项目配置（依赖、ruff、pytest） |
| [Dockerfile.template](./assets/Dockerfile.template) | 容器构建 |
| [.env.example.template](./assets/.env.example.template) | 环境变量示例 |
| [README.md.template](./assets/README.md.template) | 项目说明 |
| [.gitignore.template](./assets/.gitignore.template) | Git 忽略规则 |

### 骨架代码模板（`assets/skeleton/`）
直接复制到目标项目，无需生成：
| 文件 | 用途 |
|---|---|
| `app/main.py.template` | 应用入口（启动 MCP server） |
| `app/config/settings.py.template` | pydantic-settings 配置 |
| `app/core/logging.py.template` | logging 日志初始化 |
| `app/core/exceptions.py.template` | 自定义异常体系 |
| `app/core/mcp_server.py.template` | FastMCP server 实例 |
| `app/db/connection.py.template` | SQLAlchemy 引擎/会话 |
| `app/repositories/base_repository.py.template` | 数据访问层基类 |
| `app/repositories/example_repository.py.template` | 示例 repository（查 items 表） |
| `app/services/example_service.py.template` | 示例 service |
| `app/tools/example_tool.py.template` | 示例 MCP tool（查数据库） |
