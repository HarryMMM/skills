import json
import sys
from pathlib import Path

REQUIRED_DIRS = [
    "app", "app/api", "app/config", "app/core", "app/db", "app/models",
    "app/repositories", "app/services", "app/tools", "app/utils", "tests",
]
REQUIRED_FILES = [
    "app/main.py", "app/config/settings.py", "app/core/logging.py",
    "app/core/exceptions.py", "app/db/connection.py",
    "app/repositories/base_repository.py", "pyproject.toml",
    ".env.example",
]
FORBIDDEN_DIRS = ["evaluation", "pdm", "app/evaluation", "app/pdm"]

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    missing_dirs = [p for p in REQUIRED_DIRS if not (root / p).is_dir()]
    missing_files = [p for p in REQUIRED_FILES if not (root / p).is_file()]
    forbidden = [p for p in FORBIDDEN_DIRS if (root / p).exists()]
    result = {
        "passed": not missing_dirs and not missing_files and not forbidden,
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "forbidden_dirs": forbidden,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
