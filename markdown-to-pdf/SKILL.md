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
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage
```bash
python scripts/md_to_pdf.py <input.md>
python scripts/md_to_pdf.py <input.md> -o <output.pdf>
python scripts/md_to_pdf.py <input.md> --theme business
python scripts/md_to_pdf.py <input.md> --theme academic
python scripts/md_to_pdf.py <input.md> --theme tech
python scripts/md_to_pdf.py <input.md> --style <custom.css>
python scripts/md_to_pdf.py <input.md> --no-toc
python scripts/md_to_pdf.py <input.md> --cover --cover-author "Harry" --cover-version "v2"
python scripts/md_to_pdf.py <input.md> --header-text "Project Notes" --footer-text "Internal"
python scripts/md_to_pdf.py <input.md> --footer-style page-number
python scripts/md_to_pdf.py <input.md> --no-header-footer
python scripts/md_to_pdf.py <input.md> --browser-channel chrome
python scripts/md_to_pdf.py --config assets/config.example.json <input.md>
python scripts/md_to_pdf.py --batch-dir ./docs --batch-glob "*.md"
python scripts/md_to_pdf.py --batch-dir ./docs --batch-glob "**/*.md" --output-dir ./pdfs
python scripts/md_to_pdf.py --batch-dir ./docs --continue-on-error --report ./logs/convert-report.json
python scripts/md_to_pdf.py --batch-dir ./docs --skip-up-to-date
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
