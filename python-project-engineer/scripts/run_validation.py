"""验证编排脚本：按顺序执行所有检查并汇总输出。"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    ("结构检查", "check_structure.py"),
    ("配置检查", "check_config.py"),
    ("分层/风格检查", "check_style_conventions.py"),
    ("编译/导入冒烟检查", "smoke_check.py"),
]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    scripts_dir = Path(__file__).parent

    passed = []
    failed = []

    for name, script_file in SCRIPTS:
        script_path = scripts_dir / script_file
        if not script_path.is_file():
            failed.append({"check": name, "error": f"脚本不存在: {script_path}"})
            continue

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), str(root)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                passed.append({"check": name, "detail": result.stdout.strip()})
            else:
                detail = result.stdout.strip() or result.stderr.strip()
                failed.append({"check": name, "detail": detail})
        except subprocess.TimeoutExpired:
            failed.append({"check": name, "error": "执行超时（60s）"})
        except Exception as exc:
            failed.append({"check": name, "error": str(exc)})

    report = {
        "passed": passed,
        "failed_or_blocked": failed,
        "manual_checks_required": [
            "环境变量真实值",
            "外部数据库连通性",
            "容器在目标环境启动",
        ],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
