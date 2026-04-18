from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def ensure_frontend_built() -> None:
    dist_dir = FRONTEND_DIR / "dist"
    if dist_dir.exists():
        return
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)


def main() -> int:
    ensure_frontend_built()
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

