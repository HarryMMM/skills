import json
import re
import sys
from pathlib import Path

DB_IMPORT = re.compile(r"from\s+app\.db\b|import\s+app\.db\b")
PRINT_CALL = re.compile(r"(^|\s)print\s*\(")

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    violations = {"tool_direct_db_access": [], "api_direct_db_access": [], "service_direct_db_access": [], "print_usage": []}
    for p in root.rglob("*.py"):
        if ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8")
        if rel.startswith("app/tools/") and DB_IMPORT.search(text):
            violations["tool_direct_db_access"].append(rel)
        if rel.startswith("app/api/") and DB_IMPORT.search(text):
            violations["api_direct_db_access"].append(rel)
        if rel.startswith("app/services/") and DB_IMPORT.search(text):
            violations["service_direct_db_access"].append(rel)
        if PRINT_CALL.search(text):
            violations["print_usage"].append(rel)
    passed = all(not v for v in violations.values())
    print(json.dumps({"passed": passed, "violations": violations}, ensure_ascii=False, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
