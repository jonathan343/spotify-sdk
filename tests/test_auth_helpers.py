"""Tests for public auth helper functions."""

from __future__ import annotations

import threading

import pytest

from spotify_sdk import auth as public_auth_module
from spotify_sdk._async.auth import AsyncAuthorizationCode, TokenInfo


class TestAuthHelpers:
    @pytest.mark.anyio
    async def test_authorize_local_in_async_context_raises(self):
        auth = AsyncAuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
        )

        with pytest.raises(RuntimeError) as exc_info:
            public_auth_module._authorize_local_async_impl(
                auth,
                open_browser=False,
                authorization_url_handler=lambda _: None,
                timeout=0.5,
            )

        assert "async_authorize_local" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_async_authorize_local_runs_in_worker_thread(
        self, monkeypatch
    ):
        called_thread_names: list[str] = []

        def fake_authorize_local(
            auth: AsyncAuthorizationCode,
            *,
            state: str | None = None,
            show_dialog: bool = False,
            timeout: float = 300.0,
            open_browser: bool = True,
            authorization_url_handler=None,
        ) -> TokenInfo:
            del auth
            del state
            del show_dialog
            del timeout
            del open_browser
            del authorization_url_handler
            called_thread_names.append(threading.current_thread().name)
            return TokenInfo(
                access_token="token",
                expires_at=1_700_000_000.0,
                refresh_token="refresh",
            )

        monkeypatch.setattr(
            public_auth_module,
            "_authorize_local_async_impl",
            fake_authorize_local,
        )

        auth = AsyncAuthorizationCode(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8080/callback",
        )

        token_info = await public_auth_module.async_authorize_local(auth)

        assert token_info.access_token == "token"
        assert called_thread_names
        assert called_thread_names[0] != threading.current_thread().name
