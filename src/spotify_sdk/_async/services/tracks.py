"""Track service for Spotify API."""

from __future__ import annotations

from ...models import Track
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

    async def get_several(
        self,
        ids: list[str],
        market: str | None = None,
    ) -> list[Track]:
        """Get multiple tracks by IDs.

        Args:
            ids: List of Spotify track IDs. The Spotify API enforces a
                maximum of 20 IDs per request.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            List of tracks.

        Raises:
            ValueError: If ids is empty.
        """
        if not ids:
            raise ValueError("ids cannot be empty")
        params: dict[str, str] = {"ids": ",".join(ids)}
        if market:
            params["market"] = market
        data = await self._get("/tracks", params=params)
        return [Track.model_validate(a) for a in data["tracks"]]
