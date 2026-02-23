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

    def create(
        self,
        user_id: str,
        name: str,
        public: bool | None = None,
        collaborative: bool | None = None,
        description: str | None = None,
    ) -> SimplifiedPlaylist:
        """Create a playlist for a Spotify user.

        Args:
            user_id: The Spotify user ID that will own the playlist.
            name: The playlist name.
            public: Whether the playlist is public.
            collaborative: Whether the playlist is collaborative.
            description: Optional playlist description.

        Returns:
            The created playlist.

        Raises:
            ValueError: If user_id/name is empty, or collaborative is True
                while public is not False.
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if not name:
            raise ValueError("name cannot be empty")
        if collaborative is True and public is not False:
            raise ValueError("public must be False when collaborative is True")

        payload: dict[str, str | bool] = {"name": name}
        if public is not None:
            payload["public"] = public
        if collaborative is not None:
            payload["collaborative"] = collaborative
        if description is not None:
            payload["description"] = description

        data = self._post(f"/users/{user_id}/playlists", json=payload)
        return SimplifiedPlaylist.model_validate(data)

    def change_details(
        self,
        id: str,
        name: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
        description: str | None = None,
    ) -> None:
        """Change playlist metadata.

        Args:
            id: The Spotify playlist ID.
            name: The new playlist name.
            public: Whether the playlist should be public.
            collaborative: Whether the playlist should be collaborative.
            description: The new playlist description.

        Raises:
            ValueError: If id is empty, no fields are provided, or
                collaborative and public are both True.
        """
        if not id:
            raise ValueError("id cannot be empty")
        if (
            name is None
            and public is None
            and collaborative is None
            and description is None
        ):
            raise ValueError("At least one field must be provided")
        if collaborative is True and public is True:
            raise ValueError("public and collaborative cannot both be True")

        payload: dict[str, str | bool] = {}
        if name is not None:
            payload["name"] = name
        if public is not None:
            payload["public"] = public
        if collaborative is not None:
            payload["collaborative"] = collaborative
        if description is not None:
            payload["description"] = description

        self._put(f"/playlists/{id}", json=payload)

    def reorder_or_replace_items(
        self,
        id: str,
        uris: list[str] | None = None,
        range_start: int | None = None,
        insert_before: int | None = None,
        range_length: int | None = None,
        snapshot_id: str | None = None,
    ) -> str:
        """Reorder existing items or replace all items in a playlist.

        Args:
            id: The Spotify playlist ID.
            uris: Full replacement list of track/episode URIs.
            range_start: Start index of items to move when reordering.
            insert_before: Target index before which items are inserted.
            range_length: Number of items to move (default 1).
            snapshot_id: Playlist snapshot ID for optimistic concurrency.

        Returns:
            New playlist snapshot ID.

        Raises:
            ValueError: If id is empty, no valid mode is provided, or inputs
                for replace/reorder are mixed.
        """
        if not id:
            raise ValueError("id cannot be empty")

        endpoint = f"/playlists/{id}/tracks"
        if uris is not None:
            if (
                range_start is not None
                or insert_before is not None
                or range_length is not None
                or snapshot_id is not None
            ):
                raise ValueError(
                    "Replace mode cannot include reorder parameters"
                )
            self._validate_uris(uris)
            payload: dict[str, object] = {"uris": uris}
        else:
            if range_start is None or insert_before is None:
                raise ValueError(
                    "range_start and insert_before are required for reorder"
                )
            payload = {
                "range_start": range_start,
                "insert_before": insert_before,
            }
            if range_length is not None:
                payload["range_length"] = range_length
            if snapshot_id is not None:
                payload["snapshot_id"] = snapshot_id

        data = self._put(endpoint, json=payload)
        return self._extract_snapshot_id(data, endpoint=endpoint)

    def add_items(
        self, id: str, uris: list[str], position: int | None = None
    ) -> str:
        """Add one or more items to a playlist.

        Args:
            id: The Spotify playlist ID.
            uris: Track or episode Spotify URIs to append.
            position: Zero-based position where items should be inserted.

        Returns:
            New playlist snapshot ID.

        Raises:
            ValueError: If id is empty or uris is empty/contains empty values.
        """
        if not id:
            raise ValueError("id cannot be empty")
        self._validate_uris(uris)

        endpoint = f"/playlists/{id}/tracks"
        payload: dict[str, object] = {"uris": uris}
        if position is not None:
            payload["position"] = position

        data = self._post(endpoint, json=payload)
        return self._extract_snapshot_id(data, endpoint=endpoint)

    def remove_items(
        self,
        id: str,
        *,
        uris: list[str] | None = None,
        tracks: list[dict[str, str | list[int]]] | None = None,
        snapshot_id: str | None = None,
    ) -> str:
        """Remove one or more items from a playlist.

        Args:
            id: The Spotify playlist ID.
            uris: URIs to remove (removed wherever found).
            tracks: Explicit track objects containing `uri` and optionally
                `positions`.
            snapshot_id: Playlist snapshot ID for optimistic concurrency.

        Returns:
            New playlist snapshot ID.

        Raises:
            ValueError: If id is empty, both/neither of uris/tracks are
                provided, or track payloads are invalid.
        """
        if not id:
            raise ValueError("id cannot be empty")
        if (uris is None and tracks is None) or (
            uris is not None and tracks is not None
        ):
            raise ValueError("Provide exactly one of uris or tracks")

        if uris is not None:
            self._validate_uris(uris)
            tracks_payload: list[dict[str, str | list[int]]] = [
                {"uri": uri} for uri in uris
            ]
        else:
            tracks_payload = self._validate_tracks(tracks)

        endpoint = f"/playlists/{id}/tracks"
        payload: dict[str, object] = {"tracks": tracks_payload}
        if snapshot_id is not None:
            payload["snapshot_id"] = snapshot_id

        data = self._delete(endpoint, json=payload)
        return self._extract_snapshot_id(data, endpoint=endpoint)

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

    def upload_cover_image(self, id: str, image_base64_jpeg: str) -> None:
        """Upload a custom playlist cover image.

        Args:
            id: The Spotify playlist ID.
            image_base64_jpeg: Base64-encoded JPEG image payload.

        Raises:
            ValueError: If id or image_base64_jpeg is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        if not image_base64_jpeg:
            raise ValueError("image_base64_jpeg cannot be empty")

        self._put(
            f"/playlists/{id}/images",
            headers={"Content-Type": "image/jpeg"},
            content=image_base64_jpeg,
        )

    def _validate_uris(self, uris: list[str]) -> None:
        if not uris:
            raise ValueError("uris cannot be empty")
        if any(not uri for uri in uris):
            raise ValueError("uris cannot contain empty values")

    def _validate_tracks(
        self, tracks: list[dict[str, str | list[int]]] | None
    ) -> list[dict[str, str | list[int]]]:
        if not tracks:
            raise ValueError("tracks cannot be empty")

        for track in tracks:
            uri = track.get("uri")
            if not isinstance(uri, str) or not uri:
                raise ValueError("Each track must include a non-empty uri")
            positions = track.get("positions")
            if positions is not None and (
                not isinstance(positions, list)
                or not all(isinstance(position, int) for position in positions)
            ):
                raise ValueError("positions must be a list of integers")

        return tracks

    def _extract_snapshot_id(self, data: object, endpoint: str) -> str:
        if not isinstance(data, dict):
            raise ValueError(
                "Expected dict response from "
                f"{endpoint}, got {type(data).__name__}"
            )
        snapshot_id = data.get("snapshot_id")
        if not isinstance(snapshot_id, str):
            raise ValueError(
                f"Expected snapshot_id in response from {endpoint}"
            )
        return snapshot_id
