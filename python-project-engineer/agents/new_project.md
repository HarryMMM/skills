# 新建工程流程

## 适用场景
用户要从零创建 Python 工程脚手架。

## 引导式交互原则
- 每个步骤只问一个问题或一组紧密相关的问题
- 等待用户回答后再继续下一步
- 在关键决策点给出推荐选项
- 每完成一个阶段，向用户反馈进度

## 执行步骤

### 1. 开场说明
向用户说明接下来需要收集以下信息：
- 项目名称
- 项目类型或定位（用于推断工程形态）
- 工程创建位置
- 可选配置（有默认值，可直接跳过）

### 2. 收集基本信息
**依次询问：**

**问题 1：项目名称**
> 请问项目名称是什么？（将用于显示名和包名）

**问题 2：项目定位**
> 请用一句话描述这个项目的类型或定位。（例如："MCP 工具服务"、"REST API 后端"、"MCP + REST 混合服务"）

### 3. 推断工程形态并确认
根据用户的项目描述推断工程形态：
- 含"MCP"关键词 → `mcp` 形态（只建 `tools/`）
- 含"REST"/"API"/"HTTP"关键词 → `api` 形态（只建 `apis/`）
- 两者都包含或模糊描述 → `both` 形态（`tools/` + `apis/` 都建）

**向用户展示推断结果：**
> 根据您的描述，我建议采用 **[mcp/api/both]** 形态：
> - 将创建 `tools/` 目录 ✅ / ❌
> - 将创建 `apis/` 目录 ✅ / ❌
> 
> 是否正确？

等待用户确认或调整。

### 4. 确认工程创建位置
**问题：工程创建位置**
> 工程是直接在当前工作区目录创建，还是在当前目录下新建一个子目录？
> - **新建子目录**（推荐）：将创建 `当前目录/项目名/` 作为工程根目录
> - **当前目录**：直接在当前工作区创建所有文件

等待用户选择。

### 5. 可选配置（可跳过）
告知用户以下配置有默认值，如需调整请告知：
- Python 版本（默认 3.13）
- 作者名（默认空）

如果用户不调整，直接使用默认值。

### 6. 汇总确认
将所有收集的信息以表格形式展示：

| 配置项 | 值 |
|---|---|
| 项目名称 | xxx |
| 包名 (slug) | xxx |
| 工程形态 | mcp / api / both |
| 创建位置 | 当前目录 / 新建子目录 |
| Python 版本 | 3.13 |
| 作者 | xxx |

> 以上信息是否正确？确认后将开始创建工程。

**等待用户明确确认后才能执行后续步骤。**

### 7. 创建目录结构
根据用户选择的创建位置确定工程根目录：
- 新建子目录：工程根目录 = `当前目录/PROJECT_SLUG/`
- 当前目录：工程根目录 = 当前工作区目录

**向用户反馈：**
> 正在创建目录结构...

按 SKILL.md 中的目录结构创建目录和 `__init__.py` 文件。
根据工程形态决定：
- `mcp` 形态：创建 `app/tools/`，不创建 `app/apis/`
- `api` 形态：创建 `app/apis/`，不创建 `app/tools/`
- `both` 形态：两者都创建

始终创建的目录：`app/config/`、`app/core/`、`app/db/`、`app/models/`、`app/repositories/`、`app/services/`、`app/utils/`、`scripts/`、`tests/`

### 8. 生成配置模板文件
**向用户反馈：**
> 正在生成配置文件...

从 `assets/` 读取模板，替换 `{{变量}}` 占位符后写入目标路径：
- `pyproject.toml.template` → `pyproject.toml`
- `Dockerfile.template` → `Dockerfile`
- `.env.example.template` → `.env.example`
- `README.md.template` → `README.md`
- `.gitignore.template` → `.gitignore`

### 9. 复制骨架代码
**向用户反馈：**
> 正在复制骨架代码...

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

### 10. 执行验证
**向用户反馈：**
> 正在执行自动验证...

运行 `python scripts/run_validation.py <project_root>`，依次检查：
1. 结构检查 — 目录/文件存在性
2. 配置检查 — pyproject.toml / .env.example 关键配置
3. 分层/风格检查 — apis/tools/services 分层约束、print 检测
4. 编译/导入冒烟检查

输出固定三段：自动验证通过 / 自动验证失败或受阻 / 需要人工确认。
未执行的检查不能算通过，脚本执行失败时标记为"受阻"。

### 11. 输出结果
**向用户展示最终结果：**

1. **工程创建完成** — 列出创建的目录和文件
2. **工程形态** — 说明采用的形态（mcp / api / both）
3. **自动验证结果** — 通过/失败/受阻项
4. **人工复核清单**（如有）— 需要用户手动确认的事项
5. **下一步** — 提示用户如何启动项目

## 约束
- 禁止硬编码凭据
- 用户未确认前不得执行创建操作
