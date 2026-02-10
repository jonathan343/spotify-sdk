"""Album service for Spotify API."""

from __future__ import annotations

from ...models import Album, Page, SavedAlbum, SimplifiedAlbum, SimplifiedTrack
from .._base_service import BaseService


class AlbumService(BaseService):
    """Operations for Spotify albums."""

    def get(self, id: str, market: str | None = None) -> Album:
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
        data = self._get(f"/albums/{id}", params=params)
        return Album.model_validate(data)

    def get_several(
        self,
        ids: list[str],
        market: str | None = None,
    ) -> list[Album]:
        """Get multiple albums by IDs.

        Args:
            ids: List of Spotify album IDs. The Spotify API enforces a
                maximum of 20 IDs per request.
            market: An ISO 3166-1 alpha-2 country code for track relinking.

        Returns:
            List of albums.

        Raises:
            ValueError: If ids is empty.
        """
        if not ids:
            raise ValueError("ids cannot be empty")
        params: dict[str, str] = {"ids": ",".join(ids)}
        if market:
            params["market"] = market
        data = self._get("/albums", params=params)
        return [Album.model_validate(a) for a in data["albums"]]

    def get_tracks(
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
        data = self._get(f"/albums/{id}/tracks", params=params)
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

    def get_saved(
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
        data = self._get("/me/albums", params=params)
        return Page[SavedAlbum].model_validate(data)

    def check_saved(self, ids: list[str]) -> list[bool]:
        """Check whether albums are saved in the current user's library.

        Args:
            ids: Spotify album IDs to check.

        Returns:
            A list of booleans aligned to input ids.

        Raises:
            ValueError: If ids is empty or the response shape is invalid.
        """
        if not ids:
            raise ValueError("ids cannot be empty")
        data = self._get(
            "/me/albums/contains",
            params={"ids": ",".join(ids)},
        )
        return self._validate_bool_list_response(
            data,
            endpoint="/me/albums/contains",
        )
