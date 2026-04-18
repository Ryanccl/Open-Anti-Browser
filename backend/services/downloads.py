from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from .network import create_http_session


class DownloadRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: dict[str, dict[str, Any]] = {}

    def get_all(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return {key: value.copy() for key, value in self._tasks.items()}

    def get(self, task_key: str) -> dict[str, Any] | None:
        with self._lock:
            value = self._tasks.get(task_key)
            return value.copy() if value else None

    def start(self, task_key: str, url: str, output_path: str) -> dict[str, Any]:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and path.stat().st_size > 0:
            task = {
                "key": task_key,
                "status": "completed",
                "progress": 100,
                "downloaded_bytes": path.stat().st_size,
                "total_bytes": path.stat().st_size,
                "output_path": str(path),
                "error": "",
            }
            with self._lock:
                self._tasks[task_key] = task
            return task

        with self._lock:
            current = self._tasks.get(task_key)
            if current and current.get("status") == "running":
                return current.copy()
            self._tasks[task_key] = {
                "key": task_key,
                "status": "running",
                "progress": 0,
                "downloaded_bytes": 0,
                "total_bytes": None,
                "output_path": str(path),
                "error": "",
            }

        thread = threading.Thread(
            target=self._download_worker,
            args=(task_key, url, path),
            daemon=True,
        )
        thread.start()
        return self.get(task_key) or {}

    def _download_worker(self, task_key: str, url: str, path: Path) -> None:
        temp_path = path.with_suffix(path.suffix + ".part")
        session = create_http_session()
        try:
            response = session.get(url, stream=True)
            response.raise_for_status()
            total = int(response.headers.get("content-length", "0") or 0)
            downloaded = 0
            with temp_path.open("wb") as file_obj:
                for chunk in response.iter_content(chunk_size=1024 * 128):
                    if not chunk:
                        continue
                    file_obj.write(chunk)
                    downloaded += len(chunk)
                    progress = int(downloaded * 100 / total) if total else 0
                    self._update(
                        task_key,
                        downloaded_bytes=downloaded,
                        total_bytes=total or None,
                        progress=progress,
                    )
            temp_path.replace(path)
            self._update(
                task_key,
                status="completed",
                progress=100,
                downloaded_bytes=path.stat().st_size,
                total_bytes=path.stat().st_size,
            )
        except Exception as exc:
            self._update(task_key, status="failed", error=str(exc))
        finally:
            try:
                session.close()
            except Exception:
                pass
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception:
                pass

    def _update(self, task_key: str, **kwargs: Any) -> None:
        with self._lock:
            task = self._tasks.setdefault(task_key, {"key": task_key})
            task.update(kwargs)
