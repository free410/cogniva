"""Redis 缓存工具，Redis 不可用时自动降级为不缓存"""
import hashlib
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from core.config import settings

_client: Optional[aioredis.Redis] = None
_unavailable = False


def _get_client() -> Optional[aioredis.Redis]:
    global _client, _unavailable
    if _unavailable:
        return None
    if _client is None:
        try:
            _client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
        except Exception:
            _unavailable = True
            return None
    return _client


def make_cache_key(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


async def cache_get_json(key: str) -> Optional[Any]:
    client = _get_client()
    if client is None:
        return None
    try:
        value = await client.get(key)
    except Exception:
        return None
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


async def cache_set_json(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        await client.set(
            key,
            json.dumps(value, ensure_ascii=False, default=str),
            ex=ttl_seconds,
        )
    except Exception:
        pass


async def cache_get_int(key: str) -> int:
    client = _get_client()
    if client is None:
        return 0
    try:
        value = await client.get(key)
        return int(value) if value is not None else 0
    except Exception:
        return 0


async def cache_incr(key: str) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        await client.incr(key)
    except Exception:
        pass
