"""Tests for the Spotify client."""

import pytest

from spotify_sdk import SpotifyClient
from spotify_sdk._sync.auth import ClientCredentials
from spotify_sdk._sync.services.albums import AlbumService
from spotify_sdk._sync.services.audiobooks import SyncAudiobookService


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

    def test_has_audiobooks_service(self):
        client = SpotifyClient(access_token="test-token")
        assert hasattr(client, "audiobooks")
        assert isinstance(client.audiobooks, SyncAudiobookService)

    def test_auth_provider(self):
        auth_provider = ClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
        )
        client = SpotifyClient(auth_provider=auth_provider)
        assert client._base_client._auth_provider is auth_provider

    def test_missing_auth_raises(self):
        with pytest.raises(ValueError):
            SpotifyClient()

    def test_invalid_auth_combinations(self):
        with pytest.raises(ValueError):
            SpotifyClient(
                access_token="token",
                client_id="client-id",
                client_secret="client-secret",
            )

        with pytest.raises(ValueError):
            SpotifyClient(
                access_token="token",
                auth_provider=ClientCredentials(
                    client_id="client-id",
                    client_secret="client-secret",
                ),
            )


class TestSpotifyClientContextManager:
    def test_context_manager(self):
        with SpotifyClient(access_token="test-token") as client:
            assert isinstance(client, SpotifyClient)
