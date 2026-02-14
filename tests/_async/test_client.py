"""Tests for the Spotify client."""

import pytest

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk._async.auth import AsyncClientCredentials
from spotify_sdk._async.services.albums import AsyncAlbumService
from spotify_sdk._async.services.audiobooks import AsyncAudiobookService
from spotify_sdk._async.services.episodes import AsyncEpisodeService
from spotify_sdk._async.services.library import AsyncLibraryService
from spotify_sdk._async.services.shows import AsyncShowService
from spotify_sdk._async.services.users import AsyncUserService


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

    def test_has_audiobooks_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "audiobooks")
        assert isinstance(client.audiobooks, AsyncAudiobookService)

    def test_has_users_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "users")
        assert isinstance(client.users, AsyncUserService)

    def test_has_library_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "library")
        assert isinstance(client.library, AsyncLibraryService)

    def test_has_episodes_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "episodes")
        assert isinstance(client.episodes, AsyncEpisodeService)

    def test_has_shows_service(self):
        client = AsyncSpotifyClient(access_token="test-token")
        assert hasattr(client, "shows")
        assert isinstance(client.shows, AsyncShowService)

    def test_auth_provider(self):
        auth_provider = AsyncClientCredentials(
            client_id="client-id",
            client_secret="client-secret",
        )
        client = AsyncSpotifyClient(auth_provider=auth_provider)
        assert client._base_client._auth_provider is auth_provider

    def test_missing_auth_raises(self):
        with pytest.raises(ValueError):
            AsyncSpotifyClient()

    def test_invalid_auth_combinations(self):
        with pytest.raises(ValueError):
            AsyncSpotifyClient(
                access_token="token",
                client_id="client-id",
                client_secret="client-secret",
            )

        with pytest.raises(ValueError):
            AsyncSpotifyClient(
                access_token="token",
                auth_provider=AsyncClientCredentials(
                    client_id="client-id",
                    client_secret="client-secret",
                ),
            )


class TestSpotifyClientContextManager:
    @pytest.mark.anyio
    async def test_context_manager(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            assert isinstance(client, AsyncSpotifyClient)
