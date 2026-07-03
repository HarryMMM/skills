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
2. 项目类型或一句话定位（用于推断工程形态，见下方说明）
3. 工作模式：`new`、`refactor` 或 `feature`

### 工程形态推断
根据用户的"项目类型或一句话定位"推断需要创建哪些对外接口目录：
- 包含"MCP"关键词 → 创建 `tools/`（MCP 工具），不创建 `apis/`
- 包含"REST"/"API"/"HTTP"关键词 → 创建 `apis/`（REST API），不创建 `tools/`
- 两者都包含或模糊描述 → 同时创建 `tools/` 和 `apis/`
- 不确定时向用户确认

### 可选（默认值）
- Python 版本：默认 `3.13`
- 包名/模块名：默认由项目名规范化
- 数据库模板：默认开启（内存 SQLite）
- Docker：默认开启
- 测试骨架：默认开启
- 重构严格度：默认 `compatible`

## 工程标准

### 目录结构与职责
```text
app/
  __init__.py
  main.py              # 应用入口
  apis/                # REST API 路由（仅 api/both 形态）
    __init__.py
  config/
    __init__.py
    settings.py        # pydantic-settings 配置定义
  core/
    __init__.py
    logging.py         # logging 日志初始化
    exceptions.py      # 自定义异常
    mcp_server.py      # FastMCP server 实例
  db/
    __init__.py
    connection.py      # SQLAlchemy 引擎/会话
    seed.py            # 建表 + 种子数据逻辑
  models/
    __init__.py        # 数据模型定义
  repositories/
    __init__.py
    base_repository.py # 数据访问层基类
  services/
    __init__.py        # 业务逻辑层
  tools/               # MCP 工具（仅 mcp/both 形态）
    __init__.py
  utils/
    __init__.py
    loader.py          # 自动加载工具模块
scripts/
  seed_data.py         # 种子数据独立入口（调用 app.db.seed）
tests/
```

### 分层约束
```
tools/apis（编排入口）→ services（业务逻辑）→ repositories（数据访问）
```
- tools：MCP 工具，仅做对外编排，**禁止直接访问数据库**
- apis：REST API，仅做对外编排，**禁止直接访问数据库**
- services：实现业务逻辑，**禁止直接执行 SQL**
- repositories：承担所有数据库访问，SQL **必须参数化**

### 技术栈与约束
| 领域 | 选型 | 备注 |
|---|---|---|
| 配置 | `pydantic-settings` | 域分离，提供 `.env.example`，禁止硬编码密钥 |
| 日志 | 标准 `logging` + 彩色 Formatter | 禁止运行时 `print` |
| 数据访问 | `SQLAlchemy 2.x` async | 参数化 SQL，禁止拼接 |
| 默认数据库 | `aiosqlite`（内存 SQLite） | 开箱即用，可切换 MySQL |
| 异常 | 显式抛出 | 禁止吞异常、禁止静默失败 |
| 代码完整性 | 禁止 TODO/占位 | 所有实现必须完整可运行 |
| MCP | `mcp` SDK (FastMCP) | 自动注册 tools，支持 stdio/SSE |
| REST API | `FastAPI` + `uvicorn` | 仅 api/both 形态需要 |
| 格式化 | `ruff` | 行宽 100 |

### 建议最小配置项
```env
DEBUG=false
DB_URL=sqlite+aiosqlite:///:memory:
MCP_NAME=app-name
MCP_VERSION=1.0.0
MCP_PORT=18001
MCP_TRANSPORT=stdio
```

### 依赖基线
- 核心：`pydantic`、`pydantic-settings`、`SQLAlchemy[asyncio]`、`aiosqlite`、`mcp`
- 可选 MySQL：`aiomysql`
- 可选 REST API：`fastapi`、`uvicorn`
- 测试：`pytest`、`pytest-asyncio`
- 版本策略：稳定兼容优先，Python 默认 3.13

## 执行流程

### new：新建工程
1. 收集必填信息，推断工程形态，应用默认值
2. **向用户展示收集到的信息（含推断的工程形态），等待用户确认无误后继续**
3. 创建标准目录结构（根据工程形态决定 tools/ 和 apis/）
4. 从 [assets](./assets/) 生成模板文件（替换占位变量）
5. 复制骨架代码（启动时自动 seed，无需手动运行 seed_data.py）
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
3. 识别影响范围与落点文件（tool/route/service/repository）
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
| `app/main.py.template` | 应用入口 |
| `app/config/settings.py.template` | pydantic-settings 域分离配置 |
| `app/core/logging.py.template` | logging 日志初始化 |
| `app/core/exceptions.py.template` | 自定义异常体系 |
| `app/core/mcp_server.py.template` | FastMCP server（create + run 分离） |
| `app/db/connection.py.template` | SQLAlchemy 引擎/会话（支持 SQLite/MySQL） |
| `app/db/seed.py.template` | 建表 + 种子数据逻辑（启动时自动调用） |
| `app/utils/loader.py.template` | auto_import_tools 自动加载 |
| `app/repositories/base_repository.py.template` | 数据访问层基类 |
| `app/repositories/example_repository.py.template` | 示例 repository（查 items 表） |
| `app/services/example_service.py.template` | 示例 service |
| `app/tools/example_tool.py.template` | 示例 MCP tool（查数据库） |
| `app/apis/example_router.py.template` | 示例 FastAPI 路由（查数据库） |
| `scripts/seed_data.py.template` | 种子数据独立入口（调用 app.db.seed） |
