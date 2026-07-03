import json
import sys
from pathlib import Path

REQUIRED = {
    "pyproject.toml": ["[project]", "requires-python", "pydantic-settings", "SQLAlchemy", "aiosqlite", "mcp"],
    ".env.example": ["DB_URL", "MCP_NAME", "MCP_VERSION", "MCP_PORT", "MCP_TRANSPORT"],
}

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    issues = []
    for file, tokens in REQUIRED.items():
        path = root / file
        if not path.is_file():
            issues.append({"file": file, "error": "missing"})
            continue
        text = path.read_text(encoding="utf-8")
        miss = [t for t in tokens if t not in text]
        if miss:
            issues.append({"file": file, "missing_tokens": miss})
    result = {"passed": not issues, "issues": issues}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
