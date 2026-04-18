from __future__ import annotations

from typing import Callable


_exit_callback: Callable[[], None] | None = None
_directory_picker_callback: Callable[[str, str], str | None] | None = None


def register_exit_callback(callback: Callable[[], None] | None) -> None:
    global _exit_callback
    _exit_callback = callback


def register_directory_picker_callback(callback: Callable[[str, str], str | None] | None) -> None:
    global _directory_picker_callback
    _directory_picker_callback = callback


def request_exit_ui() -> bool:
    if _exit_callback is None:
        return False
    try:
        _exit_callback()
        return True
    except Exception:
        return False


def request_pick_directory(title: str = "", initial_dir: str = "") -> str | None:
    if _directory_picker_callback is None:
        raise RuntimeError("当前模式不支持选择文件夹")
    return _directory_picker_callback(title, initial_dir)
