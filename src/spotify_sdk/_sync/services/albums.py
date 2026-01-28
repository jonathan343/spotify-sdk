"""Album service for Spotify API."""

from __future__ import annotations

from ...models import Album, Page, SimplifiedAlbum, SimplifiedTrack
from .._base_service import BaseService


class AlbumService(BaseService):
    """Operations for Spotify albums."""

    def get(self, album_id: str, market: str | None = None) -> Album:
        """Get an album by ID.

        Args:
            album_id: The Spotify ID for the album.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            The requested album.

        Raises:
            ValueError: If album_id is empty.
        """
        if not album_id:
            raise ValueError("album_id cannot be empty")
        params = {"market": market} if market else None
        data = self._get(f"/albums/{album_id}", params=params)
        return Album.model_validate(data)

    def get_several(
        self,
        album_ids: list[str],
        market: str | None = None,
    ) -> list[Album]:
        """Get multiple albums by IDs.

        Args:
            album_ids: List of Spotify album IDs. The Spotify API enforces a
                maximum of 20 IDs per request.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            List of albums.

        Raises:
            ValueError: If album_ids is empty.
        """
        if not album_ids:
            raise ValueError("album_ids cannot be empty")
        params: dict[str, str] = {"ids": ",".join(album_ids)}
        if market:
            params["market"] = market
        data = self._get("/albums", params=params)
        return [Album.model_validate(a) for a in data["albums"]]

    def get_tracks(
        self,
        album_id: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[SimplifiedTrack]:
        """Get an album's tracks.

        Args:
            album_id: The Spotify ID for the album.
            market: An ISO 3166-1 alpha-2 country code for track relinking.
            limit: Maximum number of tracks to return (1-50, default 20).
            offset: Index of the first track to return.

        Returns:
            Paginated list of tracks.

        Raises:
            ValueError: If album_id is empty.
        """
        if not album_id:
            raise ValueError("album_id cannot be empty")
        params = {"market": market, "limit": limit, "offset": offset}
        data = self._get(f"/albums/{album_id}/tracks", params=params)
        return Page[SimplifiedTrack].model_validate(data)

    def get_new_releases(
        self, limit: int = 20, offset: int = 0
    ) -> Page[SimplifiedAlbum]:
        """Get a list of new album releases on Spotify.

        Args:
            limit: Maximum number of albums to return (1-50, default 20).
            offset: Index of the first album to return.

        Returns:
            Paginated list of new album releases.
        """
        params = {"limit": limit, "offset": offset}
        data = self._get("/browse/new-releases", params=params)
        return Page[SimplifiedAlbum].model_validate(data["albums"])
