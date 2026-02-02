"""Tests for client credentials auth."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk._async import auth as auth_module
from spotify_sdk._async.auth import AsyncClientCredentials
from spotify_sdk.exceptions import AuthenticationError


class TestClientCredentialsAuth:
    def test_env_var_defaults(self, monkeypatch):
        monkeypatch.setenv(auth_module.ENV_CLIENT_ID, "env-client-id")
        monkeypatch.setenv(auth_module.ENV_CLIENT_SECRET, "env-client-secret")
        auth = AsyncClientCredentials()
        assert auth._client_id == "env-client-id"
        assert auth._client_secret == "env-client-secret"

    def test_env_vars_ignored_with_explicit_values(self, monkeypatch):
        monkeypatch.setenv(auth_module.ENV_CLIENT_ID, "env-client-id")
        monkeypatch.setenv(auth_module.ENV_CLIENT_SECRET, "env-client-secret")
        auth = AsyncClientCredentials(
            client_id="explicit-id",
            client_secret="explicit-secret",
        )
        assert auth._client_id == "explicit-id"
        assert auth._client_secret == "explicit-secret"

    @pytest.mark.anyio
    async def test_token_fetch_and_cache(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "token-1",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        auth = AsyncClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
        )
        token_first = await auth.get_access_token()
        token_second = await auth.get_access_token()

        assert token_first == "token-1"
        assert token_second == "token-1"
        assert len(httpx_mock.get_requests()) == 1
        await auth.close()

    @pytest.mark.anyio
    async def test_token_refresh_when_expired(
        self, httpx_mock: HTTPXMock, monkeypatch
    ):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "token-1",
                "token_type": "Bearer",
                "expires_in": 1,
            },
        )
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            json={
                "access_token": "token-2",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        current_time = 1_700_000_000.0

        def fake_time():
            return current_time

        monkeypatch.setattr(auth_module.time, "time", fake_time)

        auth = AsyncClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
            skew_seconds=0,
        )
        token_first = await auth.get_access_token()
        assert token_first == "token-1"

        current_time += 5
        token_second = await auth.get_access_token()
        assert token_second == "token-2"
        assert len(httpx_mock.get_requests()) == 2
        await auth.close()

    def test_missing_fields_raises(self):
        auth = AsyncClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
        )
        with pytest.raises(AuthenticationError):
            auth._handle_response(
                auth_module.httpx.Response(200, json={"access_token": "x"})
            )

    @pytest.mark.anyio
    async def test_error_response_raises(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=auth_module.TOKEN_URL,
            status_code=400,
            json={"error": {"message": "invalid_client"}},
        )

        auth = AsyncClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
        )
        with pytest.raises(AuthenticationError):
            await auth.get_access_token()
        await auth.close()
