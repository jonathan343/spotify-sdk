"""Tests for AsyncSpotifyClient."""

from spotify_sdk import SpotifyClient
from spotify_sdk._sync.services.albums import AlbumService


class TestSpotifyClientInit:
    def test_default_values(self):
        client = SpotifyClient(access_token="test-token")
        assert client._base_client._access_token == "test-token"
        assert client._base_client._timeout == 30.0
        assert client._base_client._max_retries == 3

    def test_custom_values(self):
        client = SpotifyClient(
            access_token="test-token",
            timeout=60.0,
            max_retries=5,
        )
        assert client._base_client._timeout == 60.0
        assert client._base_client._max_retries == 5

    def test_has_albums_service(self):
        client = SpotifyClient(access_token="test-token")
        assert hasattr(client, "albums")
        assert isinstance(client.albums, AlbumService)


class TestSpotifyClientContextManager:
    def test_context_manager(self):
        with SpotifyClient(access_token="test-token") as client:
            assert isinstance(client, SpotifyClient)
