import os
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))


def main() -> None:
    _ensure_src_on_path()
    from resolve_desafios.cli import app
    app()


if __name__ == "__main__":
    main()


