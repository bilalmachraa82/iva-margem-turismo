"""
KV store helper for serverless session persistence on Vercel (Upstash KV over REST).
Falls back to in-memory if KV env vars are not present.
"""
from __future__ import annotations

import os
import json
from typing import Any, Optional

import asyncio

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None  # type: ignore


KV_URL = os.getenv("KV_REST_API_URL")
KV_TOKEN = os.getenv("KV_REST_API_TOKEN")


class KVClient:
    def __init__(self) -> None:
        self.enabled = bool(KV_URL and KV_TOKEN and httpx is not None)
        self._memory = {}

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self.enabled:
            self._memory[key] = value
            return
        headers = {"Authorization": f"Bearer {KV_TOKEN}", "Content-Type": "application/json"}
        payload = {"value": value}
        if ttl is not None:
            payload["ttl"] = ttl
        async with httpx.AsyncClient(timeout=10) as client:
            await client.put(f"{KV_URL}/set/{key}", headers=headers, json=payload)

    async def get_json(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return self._memory.get(key)
        headers = {"Authorization": f"Bearer {KV_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{KV_URL}/get/{key}", headers=headers)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            return data.get("result") if isinstance(data, dict) else None

    async def delete(self, key: str) -> None:
        if not self.enabled:
            self._memory.pop(key, None)
            return
        headers = {"Authorization": f"Bearer {KV_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(f"{KV_URL}/del/{key}", headers=headers)


# Singleton
kv = KVClient()

