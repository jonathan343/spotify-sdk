"""Playlist service for Spotify API."""

from __future__ import annotations

from ...models import Image, Page, Playlist, PlaylistTrack, SimplifiedPlaylist
from .._base_service import BaseService


class PlaylistService(BaseService):
    """Operations for Spotify playlists."""

    def get(
        self,
        id: str,
        market: str | None = None,
        fields: str | None = None,
    ) -> Playlist:
        """Get a playlist owned by a Spotify user.

        Args:
            id: The [Spotify ID](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids)
                of the playlist.
            market: An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
                If a country code is specified, only content that is available
                in that market will be returned.
            fields: Filters for the query: a comma-separated list of the fields
                to return. If omitted, all fields are returned. For example, to
                get just the playlist's description and URI: `fields=description,uri`.
                A dot separator can be used to specify non-reoccurring fields, while
                parentheses can be used to specify reoccurring fields within objects.
                For example, to get just the added date and user ID of the adder
                `fields=tracks.items(added_at,added_by.id)`. Use multiple parentheses
                to drill down into nested objects, for example
                `fields=tracks.items(track(name,href,album(name,href)))`.
                Fields can be excluded by prefixing them with an exclamation mark,
                for example: `fields=tracks.items(track(name,href,album(!name,href)))`

        Returns:
            The requested playlist.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")

        params: dict[str, str] = {}
        if market is not None:
            params["market"] = market
        if fields is not None:
            params["fields"] = fields

        data = self._get(f"/playlists/{id}", params=params)
        return Playlist.model_validate(data)

    def get_items(
        self,
        id: str,
        market: str | None = None,
        fields: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[PlaylistTrack]:
        """Get full details of the items of a playlist owned by a Spotify user.

        Args:
            id: The [Spotify ID](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids)
                of the playlist.
            market: An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
                If a country code is specified, only content that is available
                in that market will be returned.
            fields: Filters for the query: a comma-separated list of the fields
                to return. If omitted, all fields are returned. For example, to
                get just the total number of items and the request limit `fields=total,limit`.
                A dot separator can be used to specify non-reoccurring fields,
                while parentheses can be used to specify reoccurring fields
                within objects. For example, to get just the added date and
                user ID of the adder: `fields=items(added_at,added_by.id)`
                Use multiple parentheses to drill down into nested objects,
                for example: `fields=items(track(name,href,album(name,href)))`
                Fields can be excluded by prefixing them with an exclamation mark,
                for example: `fields=items.track.album(!external_urls,images)`
            limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
            offset: The index of the first item to return. Default: 0 (the first item).
                Use with limit to get the next set of items.

        Returns:
            Pages of tracks

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")

        params: dict[str, str | int] = {}
        if market is not None:
            params["market"] = market
        if fields is not None:
            params["fields"] = fields
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        data = self._get(f"/playlists/{id}/tracks", params=params)
        return Page[PlaylistTrack].model_validate(data)

    def get_for_current_user(
        self, limit: int | None = None, offset: int | None = None
    ) -> Page[SimplifiedPlaylist]:
        """Get a list of the playlists owned or followed by the current Spotify user.

        Args:
            limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
            offset: The index of the first playlist to return. Default: 0 (the first object).
                Maximum offset: 100. Use with limit to get the next set of playlists.

        Returns:
            A paged set of playlists
        """
        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = self._get("/me/playlists", params=params)
        return Page[SimplifiedPlaylist].model_validate(data)

    def get_for_user(
        self, id: str, limit: int | None = None, offset: int | None = None
    ) -> Page[SimplifiedPlaylist]:
        """Get a list of the playlists owned or followed by a Spotify user.

        Args:
            id: The user's [Spotify ID](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids).
            limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
            offset: The index of the first playlist to return. Default: 0 (the first object).
                Maximum offset: 100. Use with limit to get the next set of playlists.

        Returns:
            A paged set of playlists

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")

        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        data = self._get(f"/users/{id}/playlists", params=params)
        return Page[SimplifiedPlaylist].model_validate(data)

    def get_cover_image(self, id: str) -> list[Image]:
        """Get the current image associated with a specific playlist.

        Args:
            id: The [Spotify ID](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids)
                of the playlist.

        Returns:
            A set of images

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        data = self._get(f"/playlists/{id}/images")
        return [Image.model_validate(image) for image in data]
