"""Artist service for Spotify API."""

from __future__ import annotations

from typing import Literal, get_args

from ...models import Artist, Page, SimplifiedAlbum, Track
from .._base_service import AsyncBaseService

IncludeGroup = Literal["album", "single", "appears_on", "compilation"]
VALID_INCLUDE_GROUPS = set(get_args(IncludeGroup))


class AsyncArtistService(AsyncBaseService):
    """Operations for Spotify artists."""

    async def get(self, id: str) -> Artist:
        """Get an artist by ID.

        Args:
            id: The Spotify ID of the artist.

        Returns:
            The requested artist.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        data = await self._get(f"/artists/{id}")
        return Artist.model_validate(data)

    async def get_several(self, ids: list[str]) -> list[Artist]:
        """Get multiple artists by IDs.

        Args:
            ids: List of Spotify artist IDs. The Spotify API enforces a maximum of 50 IDs per request.

        Returns:
            The requested artists.

        Raises:
            ValueError: If ids is empty.
        """
        if not ids:
            raise ValueError("ids cannot be empty")
        data = await self._get("/artists", params={"ids": ",".join(ids)})
        return [Artist.model_validate(a) for a in data["artists"]]

    async def get_albums(
        self,
        id: str,
        include_groups: list[IncludeGroup] | None = None,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[SimplifiedAlbum]:
        """Get an artist's albums.

        Args:
            id: The Spotify ID of the artist.
            include_groups: A list of keywords to filter album types. Valid values:
                album, single, appears_on, compilation. If omitted, all types are returned.
            market: An ISO 3166-1 alpha-2 country code for the requested content.
            limit: Maximum number of albums to return (1-50, server-side default of 20).
            offset: Index of the first album to return (server-side default of 0).

        Returns:
            The albums for the requested artist.

        Raises:
            ValueError: If id is empty or include_groups contains invalid values.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params: dict[str, str | int] = {}
        if include_groups is not None:
            invalid = set(include_groups) - VALID_INCLUDE_GROUPS
            if invalid:
                raise ValueError(
                    f"Invalid include_groups: {invalid}. Valid values: {VALID_INCLUDE_GROUPS}"
                )
            params["include_groups"] = ",".join(include_groups)
        if market is not None:
            params["market"] = market
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = await self._get(f"/artists/{id}/albums", params=params)
        return Page[SimplifiedAlbum].model_validate(data)

    async def get_top_tracks(
        self, id: str, market: str | None = None
    ) -> list[Track]:
        """Get an artist's top tracks for a given market.

        Args:
            id: The Spotify ID of the artist.
            market: An ISO 3166-1 alpha-2 country code for the requested content.

        Returns:
            The top tracks for the artist.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params: dict[str, str] = {}
        if market is not None:
            params["market"] = market
        data = await self._get(f"/artists/{id}/top-tracks", params=params)
        return [Track.model_validate(a) for a in data["tracks"]]
