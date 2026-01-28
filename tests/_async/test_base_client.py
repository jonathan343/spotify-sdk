"""Tests for the base client."""

from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SpotifyError,
)
from spotify_sdk._async._base_client import AsyncBaseClient


class TestBaseClientInit:
    def test_default_values(self):
        client = AsyncBaseClient(access_token="test-token")
        assert client._access_token == "test-token"
        assert client._timeout == 30.0
        assert client._max_retries == 3

    def test_custom_values(self):
        client = AsyncBaseClient(
            access_token="test-token",
            timeout=60.0,
            max_retries=5,
        )
        assert client._timeout == 60.0
        assert client._max_retries == 5


class TestBaseClientHeaders:
    def test_default_headers(self):
        client = AsyncBaseClient(access_token="test-token")
        headers = client._default_headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"


class TestBaseClientRequest:
    @pytest.mark.anyio
    async def test_successful_get_request(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            json={"id": "123", "name": "Test Album"},
        )

        client = AsyncBaseClient(access_token="test-token")
        result = await client.request("GET", "/albums/123")

        assert result == {"id": "123", "name": "Test Album"}
        await client.close()

    @pytest.mark.anyio
    async def test_successful_post_request(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/playlists",
            method="POST",
            json={"id": "456", "name": "New Playlist"},
        )

        client = AsyncBaseClient(access_token="test-token")
        result = await client.request(
            "POST", "/playlists", json={"name": "New Playlist"}
        )

        assert result == {"id": "456", "name": "New Playlist"}
        await client.close()

    @pytest.mark.anyio
    async def test_query_params(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123?market=US",
            json={"id": "123"},
        )

        client = AsyncBaseClient(access_token="test-token")
        result = await client.request(
            "GET", "/albums/123", params={"market": "US"}
        )

        assert result == {"id": "123"}
        await client.close()

    @pytest.mark.anyio
    async def test_none_params_are_filtered(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123?market=US",
            json={"id": "123"},
        )

        client = AsyncBaseClient(access_token="test-token")
        result = await client.request(
            "GET",
            "/albums/123",
            params={"market": "US", "other": None},
        )

        assert result == {"id": "123"}
        await client.close()

    @pytest.mark.anyio
    async def test_204_returns_empty_dict(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/playlists/123",
            method="DELETE",
            status_code=204,
        )

        client = AsyncBaseClient(access_token="test-token")
        result = await client.request("DELETE", "/playlists/123")

        assert result == {}
        await client.close()


class TestBaseClientErrors:
    @pytest.mark.anyio
    async def test_400_raises_bad_request_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=400,
            json={"error": {"message": "Invalid ID"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(BadRequestError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Invalid ID"
        assert exc_info.value.status_code == 400

    @pytest.mark.anyio
    async def test_401_raises_authentication_error(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=401,
            json={"error": {"message": "Invalid token"}},
        )

        client = AsyncBaseClient(access_token="bad-token", max_retries=0)
        with pytest.raises(AuthenticationError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Invalid token"
        assert exc_info.value.status_code == 401

    @pytest.mark.anyio
    async def test_403_raises_forbidden_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=403,
            json={"error": {"message": "Access denied"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(ForbiddenError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Access denied"
        assert exc_info.value.status_code == 403

    @pytest.mark.anyio
    async def test_404_raises_not_found_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=404,
            json={"error": {"message": "Album not found"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(NotFoundError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Album not found"
        assert exc_info.value.status_code == 404

    @pytest.mark.anyio
    async def test_429_raises_rate_limit_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=429,
            headers={"Retry-After": "30"},
            json={"error": {"message": "Rate limit exceeded"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(RateLimitError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Rate limit exceeded"
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 30

    @pytest.mark.anyio
    async def test_500_raises_server_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=500,
            json={"error": {"message": "Internal error"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(ServerError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "Internal error"
        assert exc_info.value.status_code == 500

    @pytest.mark.anyio
    async def test_unknown_error_raises_spotify_error(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=418,
            json={"error": {"message": "I'm a teapot"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=0)
        with pytest.raises(SpotifyError) as exc_info:
            await client.request("GET", "/albums/123")

        assert exc_info.value.message == "I'm a teapot"
        assert exc_info.value.status_code == 418


class TestBaseClientRetry:
    @pytest.mark.anyio
    async def test_retries_on_server_error(self, httpx_mock: HTTPXMock):
        # First request fails, second succeeds
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=500,
            json={"error": {"message": "Server error"}},
        )
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            json={"id": "123", "name": "Test Album"},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=1)
        result = await client.request("GET", "/albums/123")

        assert result == {"id": "123", "name": "Test Album"}
        await client.close()

    @pytest.mark.anyio
    async def test_exhausts_retries_on_persistent_error(
        self, httpx_mock: HTTPXMock
    ):
        # All requests fail
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=500,
            json={"error": {"message": "Server error"}},
        )
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=500,
            json={"error": {"message": "Server error"}},
        )

        client = AsyncBaseClient(access_token="test-token", max_retries=1)
        with pytest.raises(ServerError):
            await client.request("GET", "/albums/123")

    @pytest.mark.anyio
    @patch("anyio.sleep")
    async def test_retries_on_rate_limit(
        self, mock_sleep, httpx_mock: HTTPXMock
    ):
        # First request returns 429, second succeeds
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=429,
            headers={"Retry-After": "2"},
            json={"error": {"message": "Rate limit exceeded"}},
        )
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            json={"id": "123", "name": "Test Album"},
        )

        async with AsyncBaseClient(
            access_token="test-token", max_retries=1
        ) as client:
            result = await client.request("GET", "/albums/123")

        assert result == {"id": "123", "name": "Test Album"}
        mock_sleep.assert_called_once_with(2)

    @pytest.mark.anyio
    @patch("anyio.sleep")
    async def test_exhausts_retries_on_persistent_rate_limit(
        self, mock_sleep, httpx_mock: HTTPXMock
    ):
        # All requests return 429
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=429,
            headers={"Retry-After": "5"},
            json={"error": {"message": "Rate limit exceeded"}},
        )
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            status_code=429,
            headers={"Retry-After": "5"},
            json={"error": {"message": "Rate limit exceeded"}},
        )

        async with AsyncBaseClient(
            access_token="test-token", max_retries=1
        ) as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.request("GET", "/albums/123")

        assert exc_info.value.retry_after == 5
        mock_sleep.assert_called_once_with(5)


class TestBaseClientContextManager:
    @pytest.mark.anyio
    async def test_context_manager(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            json={"id": "123"},
        )

        async with AsyncBaseClient(access_token="test-token") as client:
            result = await client.request("GET", "/albums/123")
            assert result == {"id": "123"}
