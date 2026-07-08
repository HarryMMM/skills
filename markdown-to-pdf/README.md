# Markdown To PDF

Convert Markdown files to polished, print-ready PDFs on Windows.

This skill uses Python with Playwright/Chromium to render Markdown through a browser-grade HTML/CSS pipeline. It is designed for reports, technical documents, academic notes, business summaries, and batch conversion of Markdown folders.

## Install

```bash
npx skills add harryMMM/skills --skill markdown-to-pdf -g
```

## Features

- Markdown to PDF conversion with browser-quality rendering
- Code block syntax highlighting
- Tables, images, links, blockquotes, lists, and footnotes
- Auto-generated table of contents
- Optional cover page
- Configurable header and footer with page numbers
- Built-in themes: `default`, `business`, `academic`, `tech`
- Batch conversion with skip/retry/report options
- Agent-friendly guided option flow

## Runtime Dependencies

After installing the skill, install the Python dependencies from the skill directory:

```powershell
pip install -r .\requirements.txt
playwright install chromium
```

## Quick Start

```powershell
python .\scripts\md_to_pdf.py .\docs\spec.md
```

## Agent Usage

Agents should not run `--interactive`. Instead, the agent should ask the user only the important choices in chat, then run the script with explicit options.

Typical guided choices:

1. Single file or batch directory
2. Input path
3. Optional output path or output directory
4. Theme: `default`, `business`, `academic`, or `tech`
5. Whether to include a cover page
6. Batch behavior when converting many files

Low-frequency options such as browser executable path, custom CSS, and retry reports use defaults unless the user asks for them.

## Examples

### Business report

```powershell
python .\scripts\md_to_pdf.py .\docs\report.md `
  --theme business `
  --cover --cover-author "Team A" --cover-version "v1" `
  --header-text "Quarterly Report" --footer-text "Internal"
```

### Batch conversion

```powershell
python .\scripts\md_to_pdf.py --batch-dir .\docs --batch-glob "*.md" --output-dir .\pdfs
```
