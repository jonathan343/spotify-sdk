"""Main Spotify client entry point."""

from __future__ import annotations

from typing import Any

from ._base_client import BaseClient
from .services.albums import AlbumService


class SpotifyClient:
    """Main client for interacting with the Spotify API.

    Example:
        >>> client = SpotifyClient(access_token="your-token")
        >>> album = client.albums.get("4aawyAB9vmqN3uQ7FjRGTy")
        >>> print(album.name)
        "To Pimp a Butterfly"

    Async Example:
        >>> async with SpotifyClient(access_token="...") as client:
        ...     album = await client.albums.get_async("4aawyAB9vmqN3uQ7FjRGTy")
    """

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

    def close(self) -> None:
        """Close the client and release resources."""
        self._base_client.close()

    async def aclose(self) -> None:
        """Close the client asynchronously."""
        await self._base_client.aclose()

    def __enter__(self) -> "SpotifyClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "SpotifyClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
