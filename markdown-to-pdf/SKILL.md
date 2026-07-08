---
name: markdown-to-pdf
description: "[Document Processing] Convert Markdown files to visually polished PDFs on Windows, with code highlighting and print-ready layout."
argument-hint: "Provide a Markdown file path, with optional PDF output path and stylesheet path"
user-invocable: true
---

# Markdown To PDF

## Skill Goal
1. Convert Markdown to accurate PDF content.
2. Produce a clean, beautiful PDF layout suitable for sharing and printing.
3. Work reliably on Windows.

## Runtime
- Python 3.10+
- Playwright with Chromium

## Runtime Dependencies
```powershell
pip install -r .\requirements.txt
playwright install chromium
```

## Usage
### Agent usage rule
Do not run `--interactive` from an agent or automation. Agent tool sessions cannot reliably answer Python `input()` prompts, so interactive mode may hang or fail. If user choices are needed, ask the user in chat first, then run the script with explicit CLI options or `--config`.

### Agent guided option flow

#### Core principle
Talk like a helpful assistant, not a CLI tool. Never output technical summaries or parameter lists. Guide the user with plain, friendly questions.

#### Conversation flow
1. **Auto-resolve** from the user's message: conversion mode, source path, output location. Only ask if genuinely missing.
2. **Ask only what matters** — and only if the user's intent differs from the default:
   - Theme → default `business`. Ask only if the user wants something different.
   - Cover page → default ON. Ask only if the user wants to skip it.
   - Table of contents → default ON. Ask only if the user wants to skip it.
   - Header & footer → default ON. Ask only if the user wants to skip it.
3. **Confirm before running** — one short sentence like "即将生成 PDF，确认吗？[Y/n]". Default Y.
4. **Run** `python .\scripts\md_to_pdf.py ...` with explicit flags.
5. **Report** the generated PDF path.

#### Good example (what the agent should say)
```
用户: 帮我把 docs/report.md 转成 PDF
Agent: 好的，我会用 business 风格生成 PDF，包含封面、目录和页眉页脚。确认生成吗？[Y/n]
用户: Y
Agent: PDF 已生成：docs/report.pdf
```

#### Bad example (what the agent must NOT say)
```
已自动识别：
转换模式：单文件
源文件：report.md
输出位置：与源文件同目录
主题：business
目录：Y
封面：N
页眉页脚：Y
```

#### Defaults (never ask)
- `--browser-channel chromium`
- no `--executable-path`
- no custom `--style`
- `--header-footer` enabled with `--footer-style page-total`
- no `--retry-failed-from`

#### Batch-only options (ask only when useful)
- Skip up-to-date → default Y
- Continue on error → default Y
- JSON report → default Y for CI / repeated runs

### Scenario: Human terminal guided flow
Use interactive mode only when a human is running the command in a real terminal. It asks questions step by step and builds options for you.
```powershell
python .\scripts\md_to_pdf.py --interactive
```

### Scenario: Quick single-file conversion
Use defaults (TOC on, clean layout, Chromium rendering).
```powershell
python .\scripts\md_to_pdf.py .\docs\spec.md
```

### Scenario: Publish-ready report (cover + business style + page footer)
```powershell
python .\scripts\md_to_pdf.py .\docs\spec.md `
  --theme business `
  --cover --cover-author "Team A" --cover-version "v2" `
  --header-text "Quarterly Report" --footer-text "Internal" --footer-style page-number
```

### Scenario: Team-standard settings for repeated runs
Store settings in JSON and only pass the input file.
```powershell
python .\scripts\md_to_pdf.py --config .\assets\config.example.json .\docs\spec.md
```

### Scenario: Convert many markdown files in one run
```powershell
python .\scripts\md_to_pdf.py --batch-dir .\docs --batch-glob "**/*.md" --output-dir .\pdfs
```

### Scenario: Large batch in CI, keep going and collect results
```powershell
python .\scripts\md_to_pdf.py --batch-dir .\docs --continue-on-error --report .\logs\convert-report.json
```

### Scenario: Speed up repeated batch runs
Skip files whose PDFs are already newer than source markdown.
```powershell
python .\scripts\md_to_pdf.py --batch-dir .\docs --skip-up-to-date
```

### Scenario: Retry only failed files from a previous run
```powershell
python .\scripts\md_to_pdf.py --batch-dir .\docs --retry-failed-from .\logs\convert-report.json
```

## Supported Markdown
- Heading, paragraph, emphasis, strikethrough
- Ordered and unordered list
- Fenced code blocks with syntax highlighting
- Tables
- Blockquotes
- Links and images
- Auto-generated table of contents (with heading anchors)
- Optional generated cover page (title/subtitle/author/version/date)
- Configurable page header and footer with page numbers
- Built-in themes: default, business, academic, tech
- JSON config mode with CLI override
- TOC page-number estimation for quick navigation in printed PDFs
- Batch reliability options: continue-on-error + JSON conversion report
- Batch acceleration and recovery: skip-up-to-date + retry-failed-from report

## Config Keys
- input, output
- batch_dir, batch_glob, output_dir
- continue_on_error, report
- skip_up_to_date, retry_failed_from
- style, theme
- toc, cover, cover_title, cover_subtitle, cover_author, cover_version, cover_date
- header_footer, header_text, footer_text, footer_style
- browser_channel, executable_path

## Notes For Windows
- This implementation uses browser-grade rendering, so CSS support is strong and output is stable.
- For Chinese text quality, ensure common CJK fonts exist on the system (for example Microsoft YaHei or SimSun).
