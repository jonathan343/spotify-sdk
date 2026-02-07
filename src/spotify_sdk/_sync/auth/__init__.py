"""Authentication helpers for the Spotify SDK."""

from __future__ import annotations

import asyncio
import base64
import inspect
import json
import os
import random
import secrets
import threading
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Awaitable, Callable, Coroutine, Protocol, TypeVar, cast
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
import sniffio
from anyio import from_thread

from ...exceptions import AuthenticationError, ServerError, SpotifyError

TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
ENV_CLIENT_ID = "SPOTIFY_SDK_CLIENT_ID"
ENV_CLIENT_SECRET = "SPOTIFY_SDK_CLIENT_SECRET"
ENV_REDIRECT_URI = "SPOTIFY_SDK_REDIRECT_URI"

_T = TypeVar("_T")
_SUCCESS_HTML = """\
<html>
  <head><title>Spotify SDK Authorization Complete</title></head>
  <body>
    <h1>Authorization complete</h1>
    <p>You can close this window now.</p>
  </body>
</html>
"""


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


class AuthProvider(Protocol):
    """Protocol for async auth providers."""

    def get_access_token(self) -> str:
        """Return a valid access token (refreshing if needed)."""
        ...

    def close(self) -> None:
        """Optional cleanup hook (default no-op)."""
        ...


class ClientCredentials:
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
        http_client: httpx.Client | None = None,
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
        self._lock = threading.Lock()
        self._client = http_client
        self._owns_client = http_client is None

    @property
    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout)
        return self._client

    def get_access_token(self) -> str:
        cached = self._token_cache.get()
        if cached and not cached.is_expired(skew_seconds=self._skew_seconds):
            return cached.access_token

        with self._lock:
            cached = self._token_cache.get()
            if cached and not cached.is_expired(
                skew_seconds=self._skew_seconds
            ):
                return cached.access_token

            token_info = self._fetch_token()
            self._token_cache.set(token_info)
            return token_info.access_token

    def _fetch_token(self) -> TokenInfo:
        auth_header = self._build_auth_header()
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._http_client.post(
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
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                raise SpotifyError(f"Connection error: {e}") from e
            except ServerError as e:
                last_exception = e
                if attempt < self._max_retries:
                    time.sleep(self._calculate_backoff(attempt))
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

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None


class AuthorizationCode:
    """Authorization code auth provider with refresh token support."""

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 0.5
    MAX_BACKOFF = 8.0
    BACKOFF_MULTIPLIER = 2

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        *,
        scope: str | list[str] | tuple[str, ...] | None = None,
        refresh_token: str | None = None,
        token_cache: TokenCache | None = None,
        timeout: float = 30.0,
        max_retries: int | None = None,
        skew_seconds: int = 30,
        http_client: httpx.Client | None = None,
    ) -> None:
        resolved_id = client_id or os.getenv(ENV_CLIENT_ID)
        resolved_secret = client_secret or os.getenv(ENV_CLIENT_SECRET)
        resolved_redirect_uri = redirect_uri or os.getenv(ENV_REDIRECT_URI)

        if not resolved_id or not resolved_secret:
            raise ValueError(
                "client_id and client_secret are required for authorization "
                "code auth."
            )
        if not resolved_redirect_uri:
            raise ValueError(
                "redirect_uri is required for authorization code auth."
            )

        self._client_id = resolved_id
        self._client_secret = resolved_secret
        self._redirect_uri = resolved_redirect_uri
        self._scope = _normalize_scope(scope)
        self._refresh_token = refresh_token
        self._timeout = timeout
        self._max_retries = (
            max_retries if max_retries is not None else self.MAX_RETRIES
        )
        self._skew_seconds = skew_seconds
        self._token_cache = token_cache or InMemoryTokenCache()
        self._lock = threading.Lock()
        self._client = http_client
        self._owns_client = http_client is None

    @property
    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout)
        return self._client

    def get_authorization_url(
        self,
        *,
        state: str | None = None,
        scope: str | list[str] | tuple[str, ...] | None = None,
        show_dialog: bool = False,
    ) -> str:
        """Build the Spotify authorization URL for user redirect."""
        resolved_scope = (
            _normalize_scope(scope) if scope is not None else self._scope
        )
        params: dict[str, str] = {
            "client_id": self._client_id,
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
        }
        if resolved_scope:
            params["scope"] = resolved_scope
        if state is not None:
            params["state"] = state
        if show_dialog:
            params["show_dialog"] = "true"
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    @staticmethod
    def parse_response_url(
        url: str,
        *,
        expected_state: str | None = None,
    ) -> str:
        """Parse callback URL and return authorization code."""
        parsed = urlparse(url)
        query = parsed.query if parsed.query else url
        values = parse_qs(query, keep_blank_values=True)

        error = _first_value(values, "error")
        if error is not None:
            error_description = _first_value(values, "error_description")
            message = f"Authorization failed: {error}"
            if error_description:
                message = f"{message} ({error_description})"
            raise AuthenticationError(
                message,
                response_body={
                    "error": error,
                    "error_description": error_description,
                },
            )

        state = _first_value(values, "state")
        if expected_state is not None and state != expected_state:
            raise AuthenticationError(
                "State mismatch in authorization response.",
                response_body={
                    "expected_state": expected_state,
                    "state": state,
                },
            )

        code = _first_value(values, "code")
        if not code:
            raise AuthenticationError(
                "Authorization response missing code.",
                response_body={"state": state},
            )
        return code

    def exchange_code(self, code: str) -> TokenInfo:
        """Exchange an authorization code for an access token."""
        if not code:
            raise ValueError("code must not be empty.")

        token_info = self._fetch_token(
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self._redirect_uri,
            },
            require_refresh_token=True,
            fallback_refresh_token=None,
        )
        self._set_token(token_info)
        return token_info

    def get_access_token(self) -> str:
        cached = self._token_cache.get()
        if (
            cached
            and cached.access_token
            and not cached.is_expired(skew_seconds=self._skew_seconds)
        ):
            return cached.access_token

        with self._lock:
            cached = self._token_cache.get()
            if (
                cached
                and cached.access_token
                and not cached.is_expired(skew_seconds=self._skew_seconds)
            ):
                return cached.access_token

            refresh_token = (
                cached.refresh_token if cached else None
            ) or self._refresh_token
            if refresh_token is None:
                raise AuthenticationError(
                    "No authorization token available. "
                    "Call exchange_code() first."
                )

            token_info = self._refresh_access_token(refresh_token)
            self._set_token(token_info)
            return token_info.access_token

    def _refresh_access_token(self, refresh_token: str) -> TokenInfo:
        return self._fetch_token(
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            require_refresh_token=False,
            fallback_refresh_token=refresh_token,
        )

    def _fetch_token(
        self,
        *,
        data: dict[str, str],
        require_refresh_token: bool,
        fallback_refresh_token: str | None,
    ) -> TokenInfo:
        auth_header = self._build_auth_header()
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._http_client.post(
                    TOKEN_URL,
                    data=data,
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                return self._handle_response(
                    response,
                    require_refresh_token=require_refresh_token,
                    fallback_refresh_token=fallback_refresh_token,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self._max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                raise SpotifyError(f"Connection error: {e}") from e
            except ServerError as e:
                last_exception = e
                if attempt < self._max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                raise

        raise last_exception or SpotifyError("Token request failed")

    def _handle_response(
        self,
        response: httpx.Response,
        *,
        require_refresh_token: bool,
        fallback_refresh_token: str | None,
    ) -> TokenInfo:
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.is_success:
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")
            refresh_token = data.get("refresh_token", fallback_refresh_token)

            if access_token is None or expires_in is None:
                raise AuthenticationError(
                    "Token response missing access_token or expires_in.",
                    response.status_code,
                    data,
                )
            if require_refresh_token and refresh_token is None:
                raise AuthenticationError(
                    "Token response missing refresh_token.",
                    response.status_code,
                    data,
                )

            try:
                expires_in_seconds = float(expires_in)
            except (TypeError, ValueError) as error:
                raise AuthenticationError(
                    "Token response has invalid expires_in.",
                    response.status_code,
                    data,
                ) from error

            return TokenInfo(
                access_token=access_token,
                expires_at=time.time() + expires_in_seconds,
                refresh_token=refresh_token,
                scope=data.get("scope", self._scope),
            )

        error_message = _extract_error_message(data)
        if response.status_code and response.status_code >= 500:
            raise ServerError(error_message, response.status_code, data)
        raise AuthenticationError(error_message, response.status_code, data)

    def _build_auth_header(self) -> str:
        raw = f"{self._client_id}:{self._client_secret}".encode("utf-8")
        encoded = base64.b64encode(raw).decode("ascii")
        return f"Basic {encoded}"

    def _set_token(self, token_info: TokenInfo) -> None:
        self._token_cache.set(token_info)
        self._refresh_token = token_info.refresh_token

    def _calculate_backoff(self, attempt: int) -> float:
        backoff = min(
            self.INITIAL_BACKOFF * (self.BACKOFF_MULTIPLIER**attempt),
            self.MAX_BACKOFF,
        )
        return backoff * (0.5 + random.random() * 0.5)

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None


class _LocalCallbackServer(HTTPServer):
    """Small callback server used by authorize_local."""

    expected_path: str
    callback_path: str | None
    received_event: threading.Event
    html_response: str


class _LocalCallbackHandler(BaseHTTPRequestHandler):
    """Capture one callback request and acknowledge in browser."""

    @property
    def _local_server(self) -> _LocalCallbackServer:
        return cast(_LocalCallbackServer, self.server)

    def do_GET(self) -> None:  # noqa: N802
        local_server = self._local_server
        request_path = urlparse(self.path).path or "/"
        if request_path != local_server.expected_path:
            self.send_error(404)
            return

        local_server.callback_path = self.path
        local_server.received_event.set()
        body = local_server.html_response.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Silence local server logs."""
        return None


def authorize_local(
    auth: AuthorizationCode,
    *,
    state: str | None = None,
    show_dialog: bool = False,
    timeout: float = 300.0,
    open_browser: bool = True,
    authorization_url_handler: Callable[[str], None] | None = None,
) -> TokenInfo:
    """Run a loopback authorization flow and exchange the callback code.

    This helper is intended for local CLI/developer workflows where the
    redirect URI points to a loopback address (`127.0.0.1` or `localhost`).
    """
    if _is_running_in_event_loop():
        raise RuntimeError(
            "authorize_local() cannot run inside an active async event loop. "
            "Use async_authorize_local() instead."
        )

    if timeout <= 0:
        raise ValueError("timeout must be greater than 0.")

    redirect = urlparse(auth._redirect_uri)
    host = redirect.hostname
    if redirect.scheme != "http":
        raise ValueError(
            "authorize_local requires an http redirect_uri on loopback."
        )
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError(
            "authorize_local requires a redirect_uri host of "
            "'127.0.0.1' or 'localhost'."
        )
    if redirect.port is None:
        raise ValueError(
            "authorize_local requires redirect_uri to include a port."
        )

    if not open_browser and authorization_url_handler is None:
        raise ValueError(
            "Set open_browser=True or provide authorization_url_handler."
        )

    resolved_state = state or secrets.token_urlsafe(24)
    authorization_url = auth.get_authorization_url(
        state=resolved_state,
        show_dialog=show_dialog,
    )

    callback_path = _wait_for_local_callback(
        host=host,
        port=redirect.port,
        expected_path=redirect.path or "/",
        authorization_url=authorization_url,
        timeout=timeout,
        open_browser=open_browser,
        authorization_url_handler=authorization_url_handler,
    )

    code = auth.parse_response_url(
        callback_path,
        expected_state=resolved_state,
    )
    return _resolve_awaitable(auth.exchange_code(code))


def _wait_for_local_callback(
    *,
    host: str,
    port: int,
    expected_path: str,
    authorization_url: str,
    timeout: float,
    open_browser: bool,
    authorization_url_handler: Callable[[str], None] | None,
) -> str:
    server = _LocalCallbackServer((host, port), _LocalCallbackHandler)
    server.expected_path = expected_path
    server.callback_path = None
    server.received_event = threading.Event()
    server.html_response = _SUCCESS_HTML

    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.1},
        daemon=True,
    )
    thread.start()

    try:
        if authorization_url_handler is not None:
            authorization_url_handler(authorization_url)

        if open_browser:
            opened = webbrowser.open(authorization_url)
            if not opened and authorization_url_handler is None:
                raise AuthenticationError(
                    "Could not open browser automatically.",
                    response_body={"authorization_url": authorization_url},
                )

        received = server.received_event.wait(timeout=timeout)
        if not received or server.callback_path is None:
            raise AuthenticationError(
                "Timed out waiting for authorization callback.",
                response_body={"timeout": timeout},
            )
        return server.callback_path
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)


def _resolve_awaitable(value: _T | Awaitable[_T]) -> _T:
    if inspect.isawaitable(value):
        awaitable = cast(Awaitable[_T], value)
        try:
            return from_thread.run(_return_awaitable, awaitable)
        except RuntimeError:
            return asyncio.run(cast(Coroutine[Any, Any, _T], awaitable))
    return value


def _return_awaitable(value: Awaitable[_T]) -> Awaitable[_T]:
    return value


def _is_running_in_event_loop() -> bool:
    try:
        sniffio.current_async_library()
    except Exception:
        return False
    return True


def _normalize_scope(
    scope: str | list[str] | tuple[str, ...] | None,
) -> str | None:
    if scope is None:
        return None
    if isinstance(scope, str):
        normalized = scope.replace(",", " ")
        return " ".join(part for part in normalized.split() if part) or None
    return " ".join(part.strip() for part in scope if part.strip()) or None


def _first_value(values: dict[str, list[str]], key: str) -> str | None:
    current = values.get(key)
    if not current:
        return None
    return current[0]


def _extract_error_message(data: dict) -> str:
    if "error" in data:
        error = data["error"]
        if isinstance(error, dict):
            return error.get("message", "Unknown error")
        return str(error)
    return "Unknown error"
