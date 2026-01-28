"""Main Spotify client entry point."""

from __future__ import annotations

from typing import Any

from ._base_client import BaseClient
from .services.albums import AlbumService
from .services.tracks import TrackService


class SpotifyClient:
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
        self._base_client = BaseClient(
            access_token=access_token,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize services
        self.albums = AlbumService(self._base_client)
        self.tracks = TrackService(self._base_client)

    def close(self) -> None:
        """Close the client and release resources."""
        self._base_client.close()

    def __enter__(self) -> "SpotifyClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
