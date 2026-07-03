# 新建工程流程

## 适用场景
用户要从零创建 Python 工程脚手架。

## 执行步骤

### 1. 信息收集与变量准备
确认以下变量值（未提供则用默认值）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `PROJECT_NAME` | 用户输入 | 项目显示名 |
| `PROJECT_SLUG` | 项目名 kebab-case 化 | 用于 pyproject.toml name |
| `PROJECT_DESCRIPTION` | 用户输入 | 一句话描述 |
| `PROJECT_LOCATION` | 当前目录下新建子目录 | 也可选择直接在当前目录创建 |
| `PYTHON_VERSION` | `3.13` | 最低 Python 版本 |
| `AUTHOR_NAME` | 空字符串 | 作者名 |

同时根据 `PROJECT_DESCRIPTION` 推断工程形态：
- 含"MCP" → `mcp` 形态（只建 `tools/`）
- 含"REST"/"API"/"HTTP" → `api` 形态（只建 `apis/`）
- 两者都有或模糊 → `both` 形态（`tools/` + `apis/` 都建）
- 不确定时向用户确认

### 2. 用户确认
将上一步收集到的所有变量值 **及推断的工程形态** 以表格形式展示给用户，等待用户确认无误后才能继续。用户未确认前不得执行后续步骤。

### 3. 创建目录结构
根据 `PROJECT_LOCATION` 确定工程根目录：
- 默认：在当前目录下创建 `PROJECT_SLUG` 子目录作为工程根目录
- 用户选择“当前目录”：直接在当前目录创建

按 SKILL.md 中的目录结构在工程根目录下创建目录和 `__init__.py` 文件。
根据工程形态决定：
- `mcp` 形态：创建 `app/tools/`，不创建 `app/apis/`
- `api` 形态：创建 `app/apis/`，不创建 `app/tools/`
- `both` 形态：两者都创建

始终创建的目录：`app/config/`、`app/core/`、`app/db/`、`app/models/`、`app/repositories/`、`app/services/`、`app/utils/`、`scripts/`、`tests/`

### 4. 生成配置模板文件
从 `assets/` 读取模板，替换 `{{变量}}` 占位符后写入目标路径：
- `pyproject.toml.template` → `pyproject.toml`
- `Dockerfile.template` → `Dockerfile`
- `.env.example.template` → `.env.example`
- `README.md.template` → `README.md`
- `.gitignore.template` → `.gitignore`

### 5. 复制骨架代码
从 `assets/skeleton/` 直接复制以下文件（无需生成，直接复制）：

**公共文件（所有形态都复制）：**
- `app/main.py.template` → `app/main.py`
- `app/config/settings.py.template` → `app/config/settings.py`
- `app/core/logging.py.template` → `app/core/logging.py`
- `app/core/exceptions.py.template` → `app/core/exceptions.py`
- `app/core/mcp_server.py.template` → `app/core/mcp_server.py`
- `app/db/connection.py.template` → `app/db/connection.py`
- `app/db/seed.py.template` → `app/db/seed.py`
- `app/utils/loader.py.template` → `app/utils/loader.py`
- `app/repositories/base_repository.py.template` → `app/repositories/base_repository.py`
- `app/repositories/example_repository.py.template` → `app/repositories/example_repository.py`
- `app/services/example_service.py.template` → `app/services/example_service.py`
- `scripts/seed_data.py.template` → `scripts/seed_data.py`

**按形态复制：**
- `mcp` 或 `both` 形态：复制 `app/tools/example_tool.py.template` → `app/tools/example_tool.py`
- `api` 或 `both` 形态：复制 `app/apis/example_router.py.template` → `app/apis/example_router.py`

另外创建空 `__init__.py`：
- `app/__init__.py`
- `app/models/__init__.py`

按形态创建：
- `mcp` 或 `both`：`app/tools/__init__.py`
- `api` 或 `both`：`app/apis/__init__.py`

### 6. 初始化测试数据
应用启动时（`python -m app.main`）会自动检测内存 SQLite 并执行建表 + 种子数据填充，无需手动运行脚本。

如需单独重新初始化，可运行：`python scripts/seed_data.py`

### 7. 执行验证
运行 `python scripts/run_validation.py <project_root>`，依次检查：
1. 结构检查 — 目录/文件存在性
2. 配置检查 — pyproject.toml / .env.example 关键配置
3. 分层/风格检查 — apis/tools/services 分层约束、print 检测
4. 编译/导入冒烟检查

输出固定三段：自动验证通过 / 自动验证失败或受阻 / 需要人工确认。
未执行的检查不能算通过，脚本执行失败时标记为"受阻"。

### 8. 输出结果
1. 目录创建结果
2. 文件生成结果
3. 工程形态说明（mcp / api / both）
4. 自动验证结果
5. 人工复核清单（如有）

## 约束
- 禁止硬编码凭据
