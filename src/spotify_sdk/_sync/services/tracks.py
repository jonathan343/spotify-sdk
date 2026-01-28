"""Track service for Spotify API."""

from __future__ import annotations

from ...models import Track
from .._base_service import BaseService


class TrackService(BaseService):
    """Operations for Spotify tracks."""

    def get(self, track_id: str, market: str | None = None) -> Track:
        """Get a track by ID.

        Args:
            track_id: The Spotify ID for the track.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            The requested track.

        Raises:
            ValueError: If track_id is empty.
        """
        if not track_id:
            raise ValueError("track_id cannot be empty")
        params = {"market": market} if market else None
        data = self._get(f"/tracks/{track_id}", params=params)
        return Track.model_validate(data)

    def get_several(
        self,
        track_ids: list[str],
        market: str | None = None,
    ) -> list[Track]:
        """Get multiple tracks by IDs.

        Args:
            track_ids: List of Spotify track IDs. The Spotify API enforces a
                maximum of 20 IDs per request.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            List of tracks.

        Raises:
            ValueError: If track_ids is empty.
        """
        if not track_ids:
            raise ValueError("track_ids cannot be empty")
        params: dict[str, str] = {"ids": ",".join(track_ids)}
        if market:
            params["market"] = market
        data = self._get("/tracks", params=params)
        return [Track.model_validate(a) for a in data["tracks"]]
