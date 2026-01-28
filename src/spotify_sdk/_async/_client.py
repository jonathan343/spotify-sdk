"""Main Spotify client entry point."""

from __future__ import annotations

from typing import Any

from ._base_client import AsyncBaseClient
from .services.albums import AsyncAlbumService
from .services.tracks import AsyncTrackService


class AsyncSpotifyClient:
    """Main client for interacting with the Spotify API."""

    def __init__(
        self,
        access_token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the Spotify client.

        Args:
            access_token: Spotify API access token.
            timeout: Default request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self._base_client = AsyncBaseClient(
            access_token=access_token,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize services
        self.albums = AsyncAlbumService(self._base_client)
        self.tracks = AsyncTrackService(self._base_client)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._base_client.close()

    async def __aenter__(self) -> "AsyncSpotifyClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
