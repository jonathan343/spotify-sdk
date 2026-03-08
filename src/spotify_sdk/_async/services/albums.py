"""Album service for Spotify API."""

from __future__ import annotations

from ...models import Album, Page, SavedAlbum, SimplifiedTrack
from .._base_service import AsyncBaseService


class AsyncAlbumService(AsyncBaseService):
    """Operations for Spotify albums."""

    async def get(self, id: str, market: str | None = None) -> Album:
        """Get an album by ID.

        Args:
            id: The Spotify ID for the album.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            The requested album.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = await self._get(f"/albums/{id}", params=params)
        return Album.model_validate(data)

    async def get_tracks(
        self,
        id: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[SimplifiedTrack]:
        """Get an album's tracks.

        Args:
            id: The Spotify ID for the album.
            market: An ISO 3166-1 alpha-2 country code for track relinking.
            limit: Maximum number of tracks to return (1-50, default 20).
            offset: Index of the first track to return.

        Returns:
            Paginated list of tracks.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market, "limit": limit, "offset": offset}
        data = await self._get(f"/albums/{id}/tracks", params=params)
        return Page[SimplifiedTrack].model_validate(data)

    async def get_saved(
        self,
        limit: int = 20,
        offset: int = 0,
        market: str | None = None,
    ) -> Page[SavedAlbum]:
        """Get albums saved in the current user's library.

        Args:
            limit: Maximum number of albums to return (1-50, default 20).
            offset: Index of the first album to return.
            market: An ISO 3166-1 alpha-2 country code.

        Returns:
            Paginated list of saved albums.
        """
        params: dict[str, int | str] = {"limit": limit, "offset": offset}
        if market is not None:
            params["market"] = market
        data = await self._get("/me/albums", params=params)
        return Page[SavedAlbum].model_validate(data)
