"""Tests for authorization code auth."""

import inspect
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, cast
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk._sync import auth as auth_module
from spotify_sdk._sync.auth import (
    AuthorizationCode,
    InMemoryTokenCache,
    TokenInfo,
)
from spotify_sdk.exceptions import AuthenticationError


def _find_free_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])
    except OSError as error:
        pytest.skip(f"Loopback bind unavailable in test environment: {error}")


class TestAuthorizationCodeAuth:
    def test_env_var_defaults(self, monkeypatch):
        monkeypatch.setenv(auth_module.ENV_CLIENT_ID, "env-client-id")
        monkeypatch.setenv(auth_module.ENV_CLIENT_SECRET, "env-client-secret")
        monkeypatch.setenv(
            auth_module.ENV_REDIRECT_URI,
            "http://127.0.0.1:8080/callback",
        )

        auth = AuthorizationCode()

        assert auth._client_id == "env-client-id"
        assert auth._client_secret == "env-client-secret"
        assert auth._redirect_uri == "http://127.0.0.1:8080/callback"

    def test_missing_redirect_uri_raises(self):
        with pytest.raises(ValueError):
            AuthorizationCode(
                client_id="client-id",
                client_secret="client-secret",
            )

    def test_get_authorization_url(self):
        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            scope=["user-read-private", "playlist-read-private"],
        )

        url = auth.get_authorization_url(
            state="state-token",
            show_dialog=True,
        )

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert parsed.netloc == "accounts.spotify.com"
        assert parsed.path == "/authorize"
        assert params["client_id"] == ["client-id"]
        assert params["response_type"] == ["code"]
        assert params["redirect_uri"] == ["http://127.0.0.1:8080/callback"]
        assert params["scope"] == ["user-read-private playlist-read-private"]
        assert params["state"] == ["state-token"]
        assert params["show_dialog"] == ["true"]

    def test_parse_response_url(self):
        code = AuthorizationCode.parse_response_url(
            "http://127.0.0.1:8080/callback?code=abc123&state=ok",
            expected_state="ok",
        )
        assert code == "abc123"

    def test_parse_response_url_state_mismatch_raises(self):
        with pytest.raises(AuthenticationError):
            AuthorizationCode.parse_response_url(
                "http://127.0.0.1:8080/callback?code=abc123&state=wrong",
                expected_state="ok",
            )

    def test_parse_response_url_error_raises(self):
        with pytest.raises(AuthenticationError):
            AuthorizationCode.parse_response_url(
                "http://127.0.0.1:8080/callback?error=access_denied",
            )

    def test_exchange_code_and_cache(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-1",
                "refresh_token": "refresh-token-1",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "user-read-private",
            },
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            scope="user-read-private",
        )

        token_info = auth.exchange_code("auth-code-1")
        token = auth.get_access_token()

        assert token == "access-token-1"
        assert token_info.access_token == "access-token-1"
        assert token_info.refresh_token == "refresh-token-1"
        assert token_info.scope == "user-read-private"

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        form = parse_qs(requests[0].content.decode())
        assert form["grant_type"] == ["authorization_code"]
        assert form["code"] == ["auth-code-1"]
        assert form["redirect_uri"] == ["http://127.0.0.1:8080/callback"]
        auth.close()

    def test_refreshes_expired_token(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-2",
                "refresh_token": "refresh-token-2",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        token_cache = InMemoryTokenCache()
        token_cache.set(
            TokenInfo(
                access_token="expired-token",
                expires_at=0,
                refresh_token="refresh-token-1",
            )
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            token_cache=token_cache,
        )

        token = auth.get_access_token()
        assert token == "access-token-2"

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        form = parse_qs(requests[0].content.decode())
        assert form["grant_type"] == ["refresh_token"]
        assert form["refresh_token"] == ["refresh-token-1"]
        auth.close()

    def test_refresh_bootstrap_from_constructor(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-3",
                "refresh_token": "refresh-token-3",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            refresh_token="refresh-token-bootstrap",
        )

        token = auth.get_access_token()
        assert token == "access-token-3"

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        form = parse_qs(requests[0].content.decode())
        assert form["grant_type"] == ["refresh_token"]
        assert form["refresh_token"] == ["refresh-token-bootstrap"]
        auth.close()

    def test_refresh_keeps_previous_refresh_token(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-4",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        token_cache = InMemoryTokenCache()
        token_cache.set(
            TokenInfo(
                access_token="expired-token",
                expires_at=0,
                refresh_token="refresh-token-keep",
            )
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            token_cache=token_cache,
        )

        token = auth.get_access_token()
        assert token == "access-token-4"

        cached_token = token_cache.get()
        assert cached_token is not None
        assert cached_token.refresh_token == "refresh-token-keep"
        auth.close()

    def test_missing_refresh_token_on_exchange_raises(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-5",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
        )

        with pytest.raises(AuthenticationError):
            auth.exchange_code("auth-code-2")
        auth.close()

    def test_get_access_token_without_bootstrap_raises(self):
        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
        )

        with pytest.raises(AuthenticationError):
            auth.get_access_token()
        auth.close()

    @pytest.mark.httpx_mock(
        should_mock=lambda request: request.url.host == "accounts.spotify.com"
    )
    def test_authorize_local_helper(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-local",
                "refresh_token": "refresh-token-local",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        port = _find_free_port()
        redirect_uri = f"http://127.0.0.1:{port}/callback"
        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri=redirect_uri,
        )

        url_ready = threading.Event()
        results: dict[str, object] = {}

        def _capture_url(url: str) -> None:
            results["authorization_url"] = url
            url_ready.set()

        def _run() -> None:
            try:
                results["token_info"] = auth_module.authorize_local(
                    auth,
                    state="local-state",
                    open_browser=False,
                    authorization_url_handler=_capture_url,
                    timeout=5.0,
                )
            except Exception as error:  # pragma: no cover - failure path
                results["error"] = error
                url_ready.set()

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        assert url_ready.wait(timeout=2.0), "authorization url not generated"

        callback_url = f"{redirect_uri}?code=auth-code-local&state=local-state"
        response = httpx.get(callback_url, timeout=5.0)
        assert response.status_code == 200

        worker.join(timeout=5.0)
        assert "error" not in results

        token_info = results.get("token_info")
        assert isinstance(token_info, TokenInfo)
        assert token_info.access_token == "access-token-local"
        assert token_info.refresh_token == "refresh-token-local"

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        form = parse_qs(requests[0].content.decode())
        assert form["grant_type"] == ["authorization_code"]
        assert form["code"] == ["auth-code-local"]
        assert form["redirect_uri"] == [redirect_uri]

    def test_authorize_local_requires_loopback_redirect(self):
        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="https://example.com/callback",
        )

        with pytest.raises(ValueError):
            auth_module.authorize_local(auth)

    def test_authorize_local_requires_open_browser_or_handler(self):
        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
        )

        with pytest.raises(ValueError):
            auth_module.authorize_local(
                auth,
                open_browser=False,
            )

    def test_concurrent_refresh_fetches_once(self, httpx_mock: HTTPXMock):
        if inspect.iscoroutinefunction(AuthorizationCode.get_access_token):
            pytest.skip(
                "Concurrent refresh in generated sync auth is covered by "
                "the unasync test variant."
            )

        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "access-token-6",
                "refresh_token": "refresh-token-6",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        token_cache = InMemoryTokenCache()
        token_cache.set(
            TokenInfo(
                access_token="expired-token",
                expires_at=0,
                refresh_token="refresh-token-1",
            )
        )

        auth = AuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
            token_cache=token_cache,
        )

        get_access_token = cast(Callable[[], str], auth.get_access_token)

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(get_access_token),
                pool.submit(get_access_token),
            ]
            tokens = [future.result() for future in futures]

        assert sorted(tokens) == ["access-token-6", "access-token-6"]
        assert len(httpx_mock.get_requests()) == 1

        close = cast(Callable[[], None], auth.close)
        close()
