import hashlib
import json
from typing import Any


# Stores cached LLM responses for the lifetime of the running app.
_LLM_RESPONSE_CACHE: dict[str, dict[str, Any]] = {}


# Builds a stable cache key from a prefix and normalized payload.
def build_cache_key(prefix: str, payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


# Returns a cached response if one exists for the key.
def get_cached_response(key: str) -> dict[str, Any] | None:
    return _LLM_RESPONSE_CACHE.get(key)


# Stores a response in the in-memory cache.
def set_cached_response(key: str, value: dict[str, Any]) -> None:
    _LLM_RESPONSE_CACHE[key] = value