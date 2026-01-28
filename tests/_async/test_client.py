"""Tests for AsyncSpotifyClient."""

import pytest

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk._async.services.albums import AsyncAlbumService


class TestSpotifyClientInit:
    def test_default_values(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert client._base_client._access_token == "test-token"
        assert client._base_client._timeout == 30.0
        assert client._base_client._max_retries == 3

    def test_custom_values(self):
        client = AsyncSpotifyClient(
            access_token="test-token",
            timeout=60.0,
            max_retries=5,
        )
        assert client._base_client._timeout == 60.0
        assert client._base_client._max_retries == 5

    def test_has_albums_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "albums")
        assert isinstance(client.albums, AsyncAlbumService)


class TestSpotifyClientContextManager:
    @pytest.mark.anyio
    async def test_context_manager(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            assert isinstance(client, AsyncSpotifyClient)
