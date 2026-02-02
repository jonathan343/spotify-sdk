"""Main Spotify client entry point."""

from __future__ import annotations

from typing import Any

from ._base_client import AsyncBaseClient
from .auth import AsyncAuthProvider, AsyncClientCredentials
from .services.albums import AsyncAlbumService
from .services.artists import AsyncArtistService
from .services.playlists import AsyncPlaylistService
from .services.tracks import AsyncTrackService


class AsyncSpotifyClient:
    """Main client for interacting with the Spotify API."""

    def __init__(
        self,
        access_token: str | None = None,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        auth_provider: AsyncAuthProvider | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the Spotify client.

        Args:
            access_token: Spotify API access token.
            client_id: Spotify API client ID.
            client_secret: Spotify API client secret.
            auth_provider: Auth provider for dynamic access tokens.
            timeout: Default request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        if auth_provider and (access_token or client_id or client_secret):
            raise ValueError(
                "Provide only one of access_token, client credentials, or "
                "auth_provider."
            )
        if access_token and (client_id or client_secret):
            raise ValueError(
                "Provide only one of access_token or client credentials."
            )

        if auth_provider is None and (client_id or client_secret):
            auth_provider = AsyncClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            )
        if auth_provider is None and access_token is None:
            raise ValueError(
                "An access_token, client credentials, or auth_provider is "
                "required."
            )

        self._base_client = AsyncBaseClient(
            access_token=access_token,
            auth_provider=auth_provider,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize services
        self.albums = AsyncAlbumService(self._base_client)
        self.tracks = AsyncTrackService(self._base_client)
        self.artists = AsyncArtistService(self._base_client)
        self.playlists = AsyncPlaylistService(self._base_client)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._base_client.close()

    @classmethod
    def from_client_credentials(
        cls,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> "AsyncSpotifyClient":
        """Create a client using the client credentials flow."""
        auth_provider = AsyncClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
        return cls(
            auth_provider=auth_provider,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def __aenter__(self) -> "AsyncSpotifyClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
