from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer


def _prompt_text(message: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{message}{suffix}: ").strip()
    if not value and default is not None:
        return default
    return value


def _prompt_yes_no(message: str, default: bool) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        value = input(f"{message} ({hint}): ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Please enter y or n.")


def _prompt_choice(message: str, choices: list[str], default: str) -> str:
    options = "/".join(choices)
    while True:
        value = input(f"{message} ({options}) [{default}]: ").strip().lower()
        if not value:
            return default
        if value in choices:
            return value
        print(f"Please choose one of: {options}")


def _run_interactive_wizard() -> dict[str, object]:
    print("Markdown to PDF interactive setup")
    mode = _prompt_choice("Conversion mode", ["single", "batch"], "single")
    config: dict[str, object] = {}

    if mode == "single":
        while True:
            input_path = _prompt_text("Input markdown file path")
            if input_path and Path(input_path).is_file():
                config["input"] = input_path
                break
            print("File not found. Please enter a valid markdown file path.")
        output_path = _prompt_text("Output PDF path (leave empty for default)")
        if output_path:
            config["output"] = output_path
    else:
        while True:
            batch_dir = _prompt_text("Batch directory path")
            if batch_dir and Path(batch_dir).is_dir():
                config["batch_dir"] = batch_dir
                break
            print("Directory not found. Please enter a valid directory.")
        config["batch_glob"] = _prompt_text("Batch glob pattern", "*.md")
        output_dir = _prompt_text("Output directory (leave empty to reuse batch dir)")
        if output_dir:
            config["output_dir"] = output_dir
        config["skip_up_to_date"] = _prompt_yes_no("Skip files that are already up-to-date", True)
        config["continue_on_error"] = _prompt_yes_no("Continue when one file fails", True)
        if _prompt_yes_no("Retry only failed files from a previous report", False):
            retry_report = _prompt_text("Retry failed from report path")
            if retry_report:
                config["retry_failed_from"] = retry_report

    config["theme"] = _prompt_choice("Theme", ["default", "business", "academic", "tech"], "business")

    config["toc"] = _prompt_yes_no("Enable table of contents", True)
    config["cover"] = _prompt_yes_no("Enable cover page", True)
    if bool(config["cover"]):
        cover_title = _prompt_text("Cover title (optional)")
        cover_subtitle = _prompt_text("Cover subtitle (optional)")
        cover_author = _prompt_text("Cover author (optional)")
        cover_version = _prompt_text("Cover version (optional)")
        cover_date = _prompt_text("Cover date (optional, example 2026-07-07)")
        if cover_title:
            config["cover_title"] = cover_title
        if cover_subtitle:
            config["cover_subtitle"] = cover_subtitle
        if cover_author:
            config["cover_author"] = cover_author
        if cover_version:
            config["cover_version"] = cover_version
        if cover_date:
            config["cover_date"] = cover_date

    config["header_footer"] = _prompt_yes_no("Enable header and footer", True)
    if bool(config["header_footer"]):
        footer_style = _prompt_choice("Footer style", ["page-total", "page-number", "none"], "page-total")
        config["footer_style"] = footer_style

    return config


def _highlight_code(code: str, lang: str | None, _attrs: str | None) -> str:
    lexer = TextLexer()
    if lang:
        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except Exception:
            lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=False, cssclass="highlight")
    return highlight(code, lexer, formatter)


def _build_markdown_renderer() -> MarkdownIt:
    md = MarkdownIt(
        "gfm-like",
        {
            "html": True,
            "typographer": True,
            "breaks": False,
            "highlight": _highlight_code,
        },
    )
    md.use(footnote_plugin)
    return md


def _load_css(css_path: Path) -> str:
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")
    return css_path.read_text(encoding="utf-8")


def _extract_first_h1(markdown_text: str) -> Optional[str]:
    match = re.search(r"^\s*#\s+(.+?)\s*$", markdown_text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def _theme_css_path(theme: str) -> Optional[Path]:
    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "themes"
    if theme == "default":
        return None
    return assets_dir / f"{theme}.css"


def _load_combined_css(theme: str, custom_css_path: Optional[Path]) -> str:
    base_css = _load_css(_default_css_path())
    theme_css = ""
    custom_css = ""

    theme_path = _theme_css_path(theme)
    if theme_path is not None:
        theme_css = _load_css(theme_path)

    if custom_css_path is not None:
        custom_css = _load_css(custom_css_path)

    return "\n\n".join([css for css in [base_css, theme_css, custom_css] if css.strip()])


def _slugify(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff\-_]+", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "section"


def _decorate_html_with_toc(body_html: str, include_toc: bool) -> str:
    soup = BeautifulSoup(body_html, "html.parser")
    heading_nodes = [
        node
        for node in soup.find_all(re.compile(r"^h[1-6]$"))
        if node.get_text(" ", strip=True)
    ]

    if not heading_nodes:
        return str(soup)

    used_ids: dict[str, int] = {}
    toc_items: list[tuple[int, str, str]] = []

    for heading in heading_nodes:
        level = int(heading.name[1])
        text = heading.get_text(" ", strip=True)
        existing_class = heading.get("class", [])
        heading["class"] = list(existing_class) + ["keep-with-next"]
        base_slug = _slugify(text)
        duplicate_count = used_ids.get(base_slug, 0)
        used_ids[base_slug] = duplicate_count + 1
        final_slug = base_slug if duplicate_count == 0 else f"{base_slug}-{duplicate_count + 1}"
        heading["id"] = final_slug
        toc_items.append((level, text, final_slug))

    if include_toc and toc_items:
        toc_nav = soup.new_tag(
            "nav",
            attrs={"class": "toc", "role": "doc-toc", "aria-label": "Table of contents"},
        )
        toc_title = soup.new_tag("h2", attrs={"class": "toc-title"})
        toc_title.string = "Table of Contents"
        toc_nav.append(toc_title)

        toc_list = soup.new_tag("ul", attrs={"class": "toc-list"})
        toc_nav.append(toc_list)

        for level, text, section_id in toc_items:
            item = soup.new_tag("li", attrs={"class": f"toc-item toc-level-{level}"})
            link = soup.new_tag("a", href=f"#{section_id}")
            link.string = text
            item.append(link)
            toc_list.append(item)

        heading_nodes[0].insert_before(toc_nav)

    return str(soup)


def _build_cover_html(
    title: str,
    subtitle: Optional[str],
    author: Optional[str],
    version: Optional[str],
    date_text: Optional[str],
) -> str:
    subtitle_html = f"<p class=\"cover-subtitle\">{html.escape(subtitle)}</p>" if subtitle else ""
    author_html = f"<p><span class=\"label\">Author</span><span>{html.escape(author)}</span></p>" if author else ""
    version_html = f"<p><span class=\"label\">Version</span><span>{html.escape(version)}</span></p>" if version else ""
    date_html = f"<p><span class=\"label\">Date</span><span>{html.escape(date_text)}</span></p>" if date_text else ""

    return (
        "<section class=\"cover-page\">"
        "<div class=\"cover-inner\">"
        f"<h1 class=\"cover-title\">{html.escape(title)}</h1>"
        f"{subtitle_html}"
        "<div class=\"cover-meta\">"
        f"{author_html}{version_html}{date_html}"
        "</div>"
        "</div>"
        "</section>"
    )


def _render_html(
    markdown_text: str,
    css_text: str,
    source_dir: Path,
    title: str,
    include_toc: bool,
    include_cover: bool,
    cover_title: Optional[str],
    cover_subtitle: Optional[str],
    cover_author: Optional[str],
    cover_version: Optional[str],
    cover_date: Optional[str],
) -> str:
    md = _build_markdown_renderer()
    body_html = md.render(markdown_text)
    body_html = _decorate_html_with_toc(body_html, include_toc)

    cover_html = ""
    if include_cover:
        resolved_cover_title = cover_title or _extract_first_h1(markdown_text) or title
        resolved_cover_date = cover_date or dt.date.today().isoformat()
        cover_html = _build_cover_html(
            title=resolved_cover_title,
            subtitle=cover_subtitle,
            author=cover_author,
            version=cover_version,
            date_text=resolved_cover_date,
        )

    # Base href allows relative image/link paths in markdown to resolve from source directory.
    base_href = source_dir.resolve().as_uri() + "/"
    escaped_title = html.escape(title)

    return (
        "<!DOCTYPE html>"
        "<html lang=\"zh-CN\">"
        "<head>"
        "<meta charset=\"utf-8\" />"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
        f"<title>{escaped_title}</title>"
        f"<base href=\"{base_href}\" />"
        f"<style>{css_text}</style>"
        "</head>"
        "<body>"
        f"{cover_html}"
        f"{body_html}"
        "</body>"
        "</html>"
    )


def _build_header_template(text: str) -> str:
    safe_text = html.escape(text)
    return (
        "<div style=\"width:100%; font-size:8px; color:#54606c; "
        "padding:0 12mm; display:flex; justify-content:space-between; "
        "align-items:center; box-sizing:border-box;\">"
        f"<span>{safe_text}</span>"
        "<span class=\"date\"></span>"
        "</div>"
    )


def _build_footer_template(text: str) -> str:
    safe_text = html.escape(text)
    return (
        "<div style=\"width:100%; font-size:8px; color:#54606c; "
        "padding:0 12mm; display:flex; justify-content:space-between; "
        "align-items:center; box-sizing:border-box;\">"
        f"<span>{safe_text}</span>"
        "<span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span>"
        "</div>"
    )


def _build_footer_template_with_style(text: str, footer_style: str) -> str:
    safe_text = html.escape(text)
    if footer_style == "page-number":
        right = "<span>Page <span class=\"pageNumber\"></span></span>"
    elif footer_style == "none":
        right = "<span></span>"
    else:
        right = "<span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span>"

    return (
        "<div style=\"width:100%; font-size:8px; color:#54606c; "
        "padding:0 12mm; display:flex; justify-content:space-between; "
        "align-items:center; box-sizing:border-box;\">"
        f"<span>{safe_text}</span>"
        f"{right}"
        "</div>"
    )


def _estimate_toc_page_numbers(page, a4_height_mm: float = 297.0) -> None:
    page.evaluate(
        """
        ({ pageHeightPx }) => {
            const tocLinks = Array.from(document.querySelectorAll('.toc-list a[href^="#"]'));
            for (const link of tocLinks) {
                const href = link.getAttribute('href') || '';
                if (!href.startsWith('#') || href.length < 2) {
                    continue;
                }
                const target = document.getElementById(href.slice(1));
                if (!target) {
                    continue;
                }
                const top = target.getBoundingClientRect().top + window.scrollY;
                const pageNumber = Math.floor(top / pageHeightPx) + 1;
                let numberNode = link.querySelector('.toc-page-number');
                if (!numberNode) {
                    numberNode = document.createElement('span');
                    numberNode.className = 'toc-page-number';
                    link.appendChild(numberNode);
                }
                numberNode.textContent = String(pageNumber);
            }
        }
        """,
        {"pageHeightPx": a4_height_mm * 96 / 25.4},
    )


def convert_markdown_to_pdf(
    input_md: Path,
    output_pdf: Path,
    custom_css_path: Optional[Path],
    theme: str,
    include_toc: bool,
    include_cover: bool,
    cover_title: Optional[str],
    cover_subtitle: Optional[str],
    cover_author: Optional[str],
    cover_version: Optional[str],
    cover_date: Optional[str],
    include_header_footer: bool,
    header_text: Optional[str],
    footer_text: Optional[str],
    footer_style: str,
    browser_channel: str,
    executable_path: Optional[Path],
) -> None:
    if not input_md.exists():
        raise FileNotFoundError(f"Markdown file not found: {input_md}")

    markdown_text = input_md.read_text(encoding="utf-8")
    css_text = _load_combined_css(theme=theme, custom_css_path=custom_css_path)
    html_doc = _render_html(
        markdown_text=markdown_text,
        css_text=css_text,
        source_dir=input_md.parent,
        title=input_md.stem,
        include_toc=include_toc,
        include_cover=include_cover,
        cover_title=cover_title,
        cover_subtitle=cover_subtitle,
        cover_author=cover_author,
        cover_version=cover_version,
        cover_date=cover_date,
    )

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        launch_options: dict[str, object] = {}
        if executable_path is not None:
            launch_options["executable_path"] = str(executable_path)
        elif browser_channel != "chromium":
            launch_options["channel"] = browser_channel

        browser = p.chromium.launch(**launch_options)
        try:
            page = browser.new_page()
            page.set_content(html_doc, wait_until="networkidle")
            if include_toc:
                _estimate_toc_page_numbers(page)

            pdf_options: dict[str, object] = {
                "path": str(output_pdf),
                "format": "A4",
                "print_background": True,
                "prefer_css_page_size": True,
                "margin": {"top": "16mm", "right": "14mm", "bottom": "16mm", "left": "14mm"},
            }

            if include_header_footer:
                pdf_options["display_header_footer"] = True
                pdf_options["header_template"] = _build_header_template(header_text or input_md.stem)
                pdf_options["footer_template"] = _build_footer_template_with_style(
                    footer_text or "Generated from Markdown",
                    footer_style,
                )
                pdf_options["margin"] = {
                    "top": "24mm",
                    "right": "14mm",
                    "bottom": "24mm",
                    "left": "14mm",
                }

            page.pdf(**pdf_options)
        finally:
            browser.close()


def _default_css_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "default.css"


def _default_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(".pdf")


def _load_config(config_path: Path) -> dict[str, object]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Config file root must be a JSON object")
    return data


def _pick_value(cli_value: object, config: dict[str, object], key: str, default: object) -> object:
    if cli_value is not None:
        return cli_value
    return config.get(key, default)


def _pick_bool(cli_value: Optional[bool], config: dict[str, object], key: str, default: bool) -> bool:
    if cli_value is not None:
        return cli_value
    raw = config.get(key, default)
    if not isinstance(raw, bool):
        raise ValueError(f"Config field '{key}' must be boolean")
    return raw


def _to_optional_path(value: object, key: str) -> Optional[Path]:
    if value is None:
        return None
    if isinstance(value, Path):
        return value
    if isinstance(value, str):
        if not value.strip():
            return None
        return Path(value)
    raise ValueError(f"Config field '{key}' must be a path string")


def _to_optional_str(value: object, key: str) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    raise ValueError(f"Config field '{key}' must be a string")


def _write_json_report(report_path: Path, payload: dict[str, object]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_failed_inputs_from_report(report_path: Path) -> set[Path]:
    if not report_path.exists():
        raise FileNotFoundError(f"Retry report not found: {report_path}")
    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Retry report must be a JSON object")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Retry report 'entries' must be an array")

    failed_inputs: set[Path] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        input_value = entry.get("input")
        if status == "failed" and isinstance(input_value, str) and input_value.strip():
            failed_inputs.add(Path(input_value).resolve())
    return failed_inputs


def _is_up_to_date(input_md: Path, output_pdf: Path) -> bool:
    if not output_pdf.exists():
        return False
    return output_pdf.stat().st_mtime >= input_md.stat().st_mtime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Markdown to a polished PDF file.")
    parser.add_argument("--config", type=Path, help="Path to JSON config file")
    parser.add_argument(
        "--interactive",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Run interactive wizard mode",
    )
    parser.add_argument("input", nargs="?", type=Path, help="Path to input markdown file")
    parser.add_argument("--batch-dir", type=Path, help="Directory containing markdown files")
    parser.add_argument(
        "--batch-glob",
        type=str,
        default=None,
        help="Glob pattern for batch mode (for example *.md or **/*.md)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for batch mode (defaults to --batch-dir)",
    )
    parser.add_argument(
        "--continue-on-error",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Continue batch conversion when a file fails",
    )
    parser.add_argument(
        "--skip-up-to-date",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Skip files when output PDF exists and is newer than markdown",
    )
    parser.add_argument(
        "--retry-failed-from",
        type=Path,
        help="Only process files marked as failed in a previous JSON report",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report path for conversion results",
    )
    parser.add_argument("-o", "--output", type=Path, help="Path to output PDF file")
    parser.add_argument(
        "--style",
        type=Path,
        help="Optional custom CSS file (loaded after base/theme styles)",
    )
    parser.add_argument(
        "--theme",
        choices=["default", "business", "academic", "tech"],
        default=None,
        help="Built-in style theme",
    )
    parser.add_argument(
        "--toc",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable automatic table of contents",
    )
    parser.add_argument(
        "--cover",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable cover page",
    )
    parser.add_argument("--cover-title", type=str, help="Cover title")
    parser.add_argument("--cover-subtitle", type=str, help="Cover subtitle")
    parser.add_argument("--cover-author", type=str, help="Cover author")
    parser.add_argument("--cover-version", type=str, help="Cover version")
    parser.add_argument("--cover-date", type=str, help="Cover date text (for example 2026-07-07)")
    parser.add_argument(
        "--header-footer",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable PDF header and footer",
    )
    parser.add_argument("--header-text", type=str, help="Custom header text")
    parser.add_argument("--footer-text", type=str, help="Custom footer text")
    parser.add_argument(
        "--footer-style",
        choices=["page-total", "page-number", "none"],
        default=None,
        help="Footer page number style",
    )
    parser.add_argument(
        "--browser-channel",
        choices=["chromium", "chrome", "msedge"],
        default=None,
        help="Browser channel for rendering. Use chrome to run with local Google Chrome.",
    )
    parser.add_argument(
        "--executable-path",
        type=Path,
        help="Optional browser executable path. Overrides --browser-channel when provided.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config: dict[str, object] = _load_config(args.config) if args.config is not None else {}

    should_start_interactive = bool(args.interactive) or (
        args.interactive is None
        and args.config is None
        and args.input is None
        and args.batch_dir is None
    )
    if should_start_interactive and not sys.stdin.isatty():
        raise SystemExit(
            "Interactive mode requires a terminal. "
            "For automation or agent use, pass explicit CLI options or a JSON config file."
        )
    wizard_config: dict[str, object] = _run_interactive_wizard() if should_start_interactive else {}
    merged_config = {**config, **wizard_config}

    input_path = _to_optional_path(_pick_value(args.input, merged_config, "input", None), "input")
    batch_dir = _to_optional_path(_pick_value(args.batch_dir, merged_config, "batch_dir", None), "batch_dir")
    batch_glob_raw = _pick_value(args.batch_glob, merged_config, "batch_glob", "*.md")
    if not isinstance(batch_glob_raw, str) or not batch_glob_raw.strip():
        raise ValueError("Config field 'batch_glob' must be a non-empty string")
    batch_glob = batch_glob_raw

    output_dir = _to_optional_path(_pick_value(args.output_dir, merged_config, "output_dir", None), "output_dir")
    continue_on_error = _pick_bool(args.continue_on_error, merged_config, "continue_on_error", False)
    skip_up_to_date = _pick_bool(args.skip_up_to_date, merged_config, "skip_up_to_date", False)
    retry_failed_from = _to_optional_path(
        _pick_value(args.retry_failed_from, merged_config, "retry_failed_from", None),
        "retry_failed_from",
    )
    report_path = _to_optional_path(_pick_value(args.report, merged_config, "report", None), "report")
    output_path = _to_optional_path(_pick_value(args.output, merged_config, "output", None), "output")
    style_path = _to_optional_path(_pick_value(args.style, merged_config, "style", None), "style")

    theme_raw = _pick_value(args.theme, merged_config, "theme", "default")
    if not isinstance(theme_raw, str) or theme_raw not in {"default", "business", "academic", "tech"}:
        raise ValueError("Config field 'theme' must be one of: default, business, academic, tech")
    theme = theme_raw

    include_toc = _pick_bool(args.toc, merged_config, "toc", True)
    include_cover = _pick_bool(args.cover, merged_config, "cover", True)

    cover_title = _to_optional_str(_pick_value(args.cover_title, merged_config, "cover_title", None), "cover_title")
    cover_subtitle = _to_optional_str(
        _pick_value(args.cover_subtitle, merged_config, "cover_subtitle", None), "cover_subtitle"
    )
    cover_author = _to_optional_str(_pick_value(args.cover_author, merged_config, "cover_author", None), "cover_author")
    cover_version = _to_optional_str(
        _pick_value(args.cover_version, merged_config, "cover_version", None), "cover_version"
    )
    cover_date = _to_optional_str(_pick_value(args.cover_date, merged_config, "cover_date", None), "cover_date")

    include_header_footer = _pick_bool(args.header_footer, merged_config, "header_footer", True)
    header_text = _to_optional_str(_pick_value(args.header_text, merged_config, "header_text", None), "header_text")
    footer_text = _to_optional_str(_pick_value(args.footer_text, merged_config, "footer_text", None), "footer_text")

    footer_style_raw = _pick_value(args.footer_style, merged_config, "footer_style", "page-total")
    if not isinstance(footer_style_raw, str) or footer_style_raw not in {
        "page-total",
        "page-number",
        "none",
    }:
        raise ValueError("Config field 'footer_style' must be one of: page-total, page-number, none")
    footer_style = footer_style_raw

    browser_channel_raw = _pick_value(args.browser_channel, merged_config, "browser_channel", "chromium")
    if not isinstance(browser_channel_raw, str) or browser_channel_raw not in {"chromium", "chrome", "msedge"}:
        raise ValueError("Config field 'browser_channel' must be one of: chromium, chrome, msedge")
    browser_channel = browser_channel_raw

    executable_path = _to_optional_path(
        _pick_value(args.executable_path, merged_config, "executable_path", None), "executable_path"
    )

    if batch_dir is not None:
        if not batch_dir.exists():
            raise FileNotFoundError(f"Batch directory not found: {batch_dir}")
        if not batch_dir.is_dir():
            raise NotADirectoryError(f"Batch path is not a directory: {batch_dir}")

        batch_files = sorted(path for path in batch_dir.glob(batch_glob) if path.is_file())
        if not batch_files:
            raise FileNotFoundError(
                f"No markdown files matched in {batch_dir} with pattern: {batch_glob}"
            )

        if retry_failed_from is not None:
            failed_set = _load_failed_inputs_from_report(retry_failed_from)
            batch_files = [p for p in batch_files if p.resolve() in failed_set]
            if not batch_files:
                raise FileNotFoundError(
                    "No files matched retry list. Check --retry-failed-from and --batch-glob settings."
                )

        resolved_output_dir = output_dir or batch_dir
        converted = 0
        failed = 0
        skipped = 0
        entries: list[dict[str, object]] = []
        for md_file in batch_files:
            rel_path = md_file.relative_to(batch_dir)
            pdf_path = (resolved_output_dir / rel_path).with_suffix(".pdf")

            if skip_up_to_date and _is_up_to_date(md_file, pdf_path):
                skipped += 1
                entries.append(
                    {
                        "input": str(md_file),
                        "output": str(pdf_path),
                        "status": "skipped",
                        "reason": "up-to-date",
                    }
                )
                print(f"PDF skipped (up-to-date): {pdf_path}")
                continue

            try:
                convert_markdown_to_pdf(
                    input_md=md_file,
                    output_pdf=pdf_path,
                    custom_css_path=style_path,
                    theme=theme,
                    include_toc=include_toc,
                    include_cover=include_cover,
                    cover_title=cover_title,
                    cover_subtitle=cover_subtitle,
                    cover_author=cover_author,
                    cover_version=cover_version,
                    cover_date=cover_date,
                    include_header_footer=include_header_footer,
                    header_text=header_text,
                    footer_text=footer_text,
                    footer_style=footer_style,
                    browser_channel=browser_channel,
                    executable_path=executable_path,
                )
                converted += 1
                entries.append(
                    {
                        "input": str(md_file),
                        "output": str(pdf_path),
                        "status": "success",
                    }
                )
                print(f"PDF generated: {pdf_path}")
            except Exception as e:
                failed += 1
                entries.append(
                    {
                        "input": str(md_file),
                        "output": str(pdf_path),
                        "status": "failed",
                        "error": str(e),
                    }
                )
                print(f"PDF failed: {md_file} -> {e}")
                if not continue_on_error:
                    break

        summary = {
            "mode": "batch",
            "converted": converted,
            "failed": failed,
            "skipped": skipped,
            "total": len(entries),
            "entries": entries,
        }
        if report_path is not None:
            _write_json_report(report_path, summary)
            print(f"Report written: {report_path}")

        print(
            "Batch conversion completed. "
            f"Success: {converted}, Failed: {failed}, Skipped: {skipped}, Total processed: {len(entries)}"
        )
        if failed > 0 and not continue_on_error:
            raise RuntimeError("Batch conversion stopped on first failure. Use --continue-on-error to keep going.")
        return

    if input_path is None:
        raise ValueError("Provide either <input> for single file mode or --batch-dir for batch mode.")

    if output_path is None:
        output_path = _default_output_path(input_path)

    convert_markdown_to_pdf(
        input_md=input_path,
        output_pdf=output_path,
        custom_css_path=style_path,
        theme=theme,
        include_toc=include_toc,
        include_cover=include_cover,
        cover_title=cover_title,
        cover_subtitle=cover_subtitle,
        cover_author=cover_author,
        cover_version=cover_version,
        cover_date=cover_date,
        include_header_footer=include_header_footer,
        header_text=header_text,
        footer_text=footer_text,
        footer_style=footer_style,
        browser_channel=browser_channel,
        executable_path=executable_path,
    )
    print(f"PDF generated: {output_path}")

    if report_path is not None:
        _write_json_report(
            report_path,
            {
                "mode": "single",
                "converted": 1,
                "failed": 0,
                "total": 1,
                "entries": [
                    {
                        "input": str(input_path),
                        "output": str(output_path),
                        "status": "success",
                    }
                ],
            },
        )
        print(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
