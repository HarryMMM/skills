import compileall
import importlib
import json
import sys
from pathlib import Path

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(root))
    compile_ok = compileall.compile_dir(str(root / "app"), quiet=1)
    import_ok = True
    import_error = None
    try:
        importlib.import_module("app.main")
    except Exception as exc:  # noqa: BLE001
        import_ok = False
        import_error = str(exc)
    passed = bool(compile_ok and import_ok)
    print(json.dumps({"passed": passed, "compile_ok": bool(compile_ok), "import_ok": import_ok, "import_error": import_error}, ensure_ascii=False, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
