"""Shared auth cache types used by sync and async auth providers."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TokenInfo:
    """Cached access token with expiry."""

    access_token: str
    expires_at: float
    refresh_token: str | None = None
    scope: str | None = None

    def is_expired(self, *, skew_seconds: int) -> bool:
        """Return True if the token is expired or within the skew window."""
        return time.time() >= (self.expires_at - skew_seconds)


class TokenCache(Protocol):
    """Token cache interface."""

    def get(self) -> TokenInfo | None:
        """Return a cached token or None if missing."""

    def set(self, token: TokenInfo) -> None:
        """Store a token in the cache."""


class InMemoryTokenCache:
    """Simple in-memory token cache."""

    def __init__(self) -> None:
        self._token: TokenInfo | None = None

    def get(self) -> TokenInfo | None:
        return self._token

    def set(self, token: TokenInfo) -> None:
        self._token = token


class FileTokenCache:
    """JSON file-backed token cache."""

    def __init__(self, path: str = ".spotify_sdk_token.json") -> None:
        self._path = Path(path).expanduser()

    def get(self) -> TokenInfo | None:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError):
            return None

        access_token = payload.get("access_token")
        expires_at = payload.get("expires_at")
        if not isinstance(access_token, str):
            return None

        try:
            expires_at_value = float(expires_at)
        except (TypeError, ValueError):
            return None

        refresh_token = payload.get("refresh_token")
        if refresh_token is not None and not isinstance(refresh_token, str):
            refresh_token = None

        scope = payload.get("scope")
        if scope is not None and not isinstance(scope, str):
            scope = None

        return TokenInfo(
            access_token=access_token,
            expires_at=expires_at_value,
            refresh_token=refresh_token,
            scope=scope,
        )

    def set(self, token: TokenInfo) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "access_token": token.access_token,
            "expires_at": token.expires_at,
            "refresh_token": token.refresh_token,
            "scope": token.scope,
        }
        self._path.write_text(
            json.dumps(payload, separators=(",", ":")),
            encoding="utf-8",
        )
        try:
            os.chmod(self._path, 0o600)
        except OSError:
            pass
