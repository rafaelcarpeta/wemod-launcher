#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
from datetime import datetime, timezone
from typing import Any


class LogManager:
    # NOTE: Not a real implementation. May be replaced with Python's built-in
    # logging module if that makes more sense. Should have timestamps and
    # structured type/level output.

    def __init__(self, settings: Any) -> None:
        self._subscribers: list[dict[str, Any]] = []
        self._log_path = settings.log_path
        self._ensure_log_dir()
        self._write_header()

    def _ensure_log_dir(self) -> None:
        os.makedirs(os.path.dirname(self._log_path), exist_ok=True)

    def _write_header(self) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        try:
            import sys as _sys

            ver = _sys.version
        except Exception:
            ver = "unknown"
        with open(self._log_path, "w") as f:
            f.write(f"# Wand Launcher Log — {ts}\n")
            f.write(f"# Python {ver}\n#\n")

    def info(self, type_: str, message: str) -> None:
        self.emit(type_, "info", message)

    def error(self, type_: str, message: str) -> None:
        self.emit(type_, "error", message)

    def emit(self, type_: str, level: str, message: str) -> None:
        line = f"[{level}] {type_}: {message}\n"
        with open(self._log_path, "a") as f:
            f.write(line)
        for sub in self._subscribers:
            if self._matches(sub, type_, level):
                sub["fn"](type_, level, message)

    def subscribe(self, fn: Any, type_filter: str = "", level_filter: str = "") -> None:
        self._subscribers.append({"fn": fn, "type": type_filter, "level": level_filter})

    def _matches(self, sub: dict[str, Any], type_: str, level: str) -> bool:
        if sub["level"] and sub["level"] != level:
            return False
        if sub["type"] and sub["type"] not in type_:
            return False
        return True
