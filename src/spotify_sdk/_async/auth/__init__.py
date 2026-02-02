"""Authentication helpers for the Spotify SDK."""

from __future__ import annotations

import base64
import os
import random
import time
from dataclasses import dataclass
from typing import Protocol

import anyio
import httpx

from ...exceptions import AuthenticationError, ServerError, SpotifyError

TOKEN_URL = "https://accounts.spotify.com/api/token"
ENV_CLIENT_ID = "SPOTIFY_SDK_CLIENT_ID"
ENV_CLIENT_SECRET = "SPOTIFY_SDK_CLIENT_SECRET"


@dataclass(frozen=True)
class TokenInfo:
    """Cached access token with expiry."""

    access_token: str
    expires_at: float

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


class AsyncAuthProvider(Protocol):
    """Protocol for async auth providers."""

    async def get_access_token(self) -> str:
        """Return a valid access token (refreshing if needed)."""
        ...

    async def close(self) -> None:
        """Optional cleanup hook (default no-op)."""
        ...


class AsyncClientCredentials:
    """Client credentials auth provider."""

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 0.5
    MAX_BACKOFF = 8.0
    BACKOFF_MULTIPLIER = 2

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        *,
        token_cache: TokenCache | None = None,
        timeout: float = 30.0,
        max_retries: int | None = None,
        skew_seconds: int = 30,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        resolved_id = client_id or os.getenv(ENV_CLIENT_ID)
        resolved_secret = client_secret or os.getenv(ENV_CLIENT_SECRET)

        if not resolved_id or not resolved_secret:
            raise ValueError(
                "client_id and client_secret are required for client "
                "credentials auth."
            )

        self._client_id = resolved_id
        self._client_secret = resolved_secret
        self._timeout = timeout
        self._max_retries = (
            max_retries if max_retries is not None else self.MAX_RETRIES
        )
        self._skew_seconds = skew_seconds
        self._token_cache = token_cache or InMemoryTokenCache()
        self._lock = anyio.Lock()
        self._client = http_client
        self._owns_client = http_client is None

    @property
    def _http_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def get_access_token(self) -> str:
        cached = self._token_cache.get()
        if cached and not cached.is_expired(skew_seconds=self._skew_seconds):
            return cached.access_token

        async with self._lock:
            cached = self._token_cache.get()
            if cached and not cached.is_expired(
                skew_seconds=self._skew_seconds
            ):
                return cached.access_token

            token_info = await self._fetch_token()
            self._token_cache.set(token_info)
            return token_info.access_token

    async def _fetch_token(self) -> TokenInfo:
        auth_header = self._build_auth_header()
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._http_client.post(
                    TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                return self._handle_response(response)
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self._max_retries:
                    await anyio.sleep(self._calculate_backoff(attempt))
                    continue
                raise SpotifyError(f"Connection error: {e}") from e
            except ServerError as e:
                last_exception = e
                if attempt < self._max_retries:
                    await anyio.sleep(self._calculate_backoff(attempt))
                    continue
                raise

        raise last_exception or SpotifyError("Token request failed")

    def _handle_response(self, response: httpx.Response) -> TokenInfo:
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.is_success:
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")
            if access_token is None or expires_in is None:
                raise AuthenticationError(
                    "Token response missing access_token or expires_in.",
                    response.status_code,
                    data,
                )
            return TokenInfo(
                access_token=access_token,
                expires_at=time.time() + float(expires_in),
            )

        error_message = _extract_error_message(data)
        if response.status_code and response.status_code >= 500:
            raise ServerError(error_message, response.status_code, data)
        raise AuthenticationError(error_message, response.status_code, data)

    def _build_auth_header(self) -> str:
        raw = f"{self._client_id}:{self._client_secret}".encode("utf-8")
        encoded = base64.b64encode(raw).decode("ascii")
        return f"Basic {encoded}"

    def _calculate_backoff(self, attempt: int) -> float:
        backoff = min(
            self.INITIAL_BACKOFF * (self.BACKOFF_MULTIPLIER**attempt),
            self.MAX_BACKOFF,
        )
        return backoff * (0.5 + random.random() * 0.5)

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None


def _extract_error_message(data: dict) -> str:
    if "error" in data:
        error = data["error"]
        if isinstance(error, dict):
            return error.get("message", "Unknown error")
        return str(error)
    return "Unknown error"
