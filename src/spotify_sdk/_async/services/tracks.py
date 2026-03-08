"""Track service for Spotify API."""

from __future__ import annotations

from ...models import Page, SavedTrack, Track
from .._base_service import AsyncBaseService


class AsyncTrackService(AsyncBaseService):
    """Operations for Spotify tracks."""

    async def get(self, id: str, market: str | None = None) -> Track:
        """Get a track by ID.

        Args:
            id: The Spotify ID for the track.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            The requested track.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = await self._get(f"/tracks/{id}", params=params)
        return Track.model_validate(data)

    async def get_saved(
        self,
        limit: int = 20,
        offset: int = 0,
        market: str | None = None,
    ) -> Page[SavedTrack]:
        """Get tracks saved in the current user's library.

        Args:
            limit: Maximum number of tracks to return (1-50, default 20).
            offset: Index of the first track to return.
            market: An ISO 3166-1 alpha-2 country code.

        Returns:
            Paginated list of saved tracks.
        """
        params: dict[str, int | str] = {"limit": limit, "offset": offset}
        if market is not None:
            params["market"] = market
        data = await self._get("/me/tracks", params=params)
        return Page[SavedTrack].model_validate(data)
