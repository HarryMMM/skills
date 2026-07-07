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

## Install
Install the skill:
```bash
npx skills add harryMMM/skills --skill markdown-to-pdf -g
```

Install runtime dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage
### Scenario: You want a guided flow (recommended for new users)
Use interactive mode. It asks questions step by step and builds options for you.
```bash
python scripts/md_to_pdf.py --interactive
```

### Scenario: Quick single-file conversion
Use defaults (TOC on, clean layout, Chromium rendering).
```bash
python scripts/md_to_pdf.py ./docs/spec.md
```

### Scenario: Publish-ready report (cover + business style + page footer)
```bash
python scripts/md_to_pdf.py ./docs/spec.md \
	--theme business \
	--cover --cover-author "Team A" --cover-version "v2" \
	--header-text "Quarterly Report" --footer-text "Internal" --footer-style page-number
```

### Scenario: Team-standard settings for repeated runs
Store settings in JSON and only pass the input file.
```bash
python scripts/md_to_pdf.py --config assets/config.example.json ./docs/spec.md
```

### Scenario: Convert many markdown files in one run
```bash
python scripts/md_to_pdf.py --batch-dir ./docs --batch-glob "**/*.md" --output-dir ./pdfs
```

### Scenario: Large batch in CI, keep going and collect results
```bash
python scripts/md_to_pdf.py --batch-dir ./docs --continue-on-error --report ./logs/convert-report.json
```

### Scenario: Speed up repeated batch runs
Skip files whose PDFs are already newer than source markdown.
```bash
python scripts/md_to_pdf.py --batch-dir ./docs --skip-up-to-date
```

### Scenario: Retry only failed files from a previous run
```bash
python scripts/md_to_pdf.py --batch-dir ./docs --retry-failed-from ./logs/convert-report.json
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
