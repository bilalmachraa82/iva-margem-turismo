"""Session storage helpers to share state across Uvicorn workers."""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class FileSessionStore:
    """Persist session payloads on disk so multiple workers share state."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        safe_id = session_id.replace("/", "_")
        return self.base_dir / f"{safe_id}.json"

    async def set(self, session_id: str, value: Dict[str, Any]) -> None:
        await asyncio.to_thread(self._write_file, session_id, value)

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self._read_file, session_id)

    async def delete(self, session_id: str) -> None:
        await asyncio.to_thread(self._delete_file, session_id)

    async def clear(self) -> None:
        await asyncio.to_thread(self._clear_files)

    def purge_expired(self, max_age: timedelta) -> int:
        """Delete sessions older than ``max_age``. Returns number of files removed."""
        removed = 0
        now = datetime.now()
        for path in self.base_dir.glob("*.json"):
            try:
                if now - datetime.fromtimestamp(path.stat().st_mtime) > max_age:
                    path.unlink()
                    removed += 1
            except FileNotFoundError:
                continue
        return removed

    # ----- private helpers -----
    def _write_file(self, session_id: str, value: Dict[str, Any]) -> None:
        path = self._session_path(session_id)
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(value, fh, ensure_ascii=False)
        os.replace(tmp_path, path)

    def _read_file(self, session_id: str) -> Optional[Dict[str, Any]]:
        path = self._session_path(session_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _delete_file(self, session_id: str) -> None:
        path = self._session_path(session_id)
        try:
            path.unlink()
        except FileNotFoundError:
            return

    def _clear_files(self) -> None:
        for path in self.base_dir.glob("*.json"):
            try:
                path.unlink()
            except FileNotFoundError:
                continue
