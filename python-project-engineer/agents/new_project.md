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
| `PYTHON_VERSION` | `3.13` | 最低 Python 版本 |
| `AUTHOR_NAME` | 空字符串 | 作者名 |

### 2. 创建目录结构
按 SKILL.md 中的目录结构创建所有目录和 `__init__.py` 文件。

### 3. 生成配置模板文件
从 `assets/` 读取模板，替换 `{{变量}}` 占位符后写入目标路径：
- `pyproject.toml.template` → `pyproject.toml`
- `Dockerfile.template` → `Dockerfile`
- `.env.example.template` → `.env.example`
- `README.md.template` → `README.md`
- `ci-github.yml.template` → `.github/workflows/ci.yml`
- `.gitignore.template` → `.gitignore`

### 4. 复制骨架代码
从 `assets/skeleton/` 直接复制以下文件（无需生成，直接复制）：
- `app/main.py.template` → `app/main.py`
- `app/config/settings.py.template` → `app/config/settings.py`
- `app/core/logging.py.template` → `app/core/logging.py`
- `app/core/exceptions.py.template` → `app/core/exceptions.py`
- `app/db/connection.py.template` → `app/db/connection.py`
- `app/repositories/base_repository.py.template` → `app/repositories/base_repository.py`

另外创建空文件：
- `app/__init__.py`
- `app/api/__init__.py`
- `app/models/__init__.py`
- `app/services/__init__.py`
- `app/tools/__init__.py`
- `app/utils/__init__.py`

### 5. 执行验证
运行 `python scripts/run_validation.py <project_root>`，依次检查：
1. 结构检查 — 目录/文件存在性、禁止目录
2. 配置检查 — pyproject.toml / .env.example 关键配置
3. 分层/风格检查 — api/tools/services 分层约束、print 检测
4. 编译/导入冒烟检查

输出固定三段：自动验证通过 / 自动验证失败或受阻 / 需要人工确认。
未执行的检查不能算通过，脚本执行失败时标记为“受阻”。

### 6. 输出结果
1. 目录创建结果
2. 文件生成结果
3. 自动验证结果
4. 人工复核清单（如有）

## 约束
- 禁止硬编码凭据
