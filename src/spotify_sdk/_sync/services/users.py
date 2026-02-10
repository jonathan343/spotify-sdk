"""User service for Spotify API."""

from __future__ import annotations

from typing import Literal, get_args

from ...models import Artist, CurrentUser, CursorPage, Page, Track
from .._base_service import BaseService

TimeRange = Literal["long_term", "medium_term", "short_term"]
VALID_TIME_RANGES = set(get_args(TimeRange))
FollowType = Literal["artist", "user"]
VALID_FOLLOW_TYPES = set(get_args(FollowType))


class UserService(BaseService):
    """Operations for Spotify users."""

    def get_current_profile(self) -> CurrentUser:
        """Get detailed profile information about the current user.

        Returns:
            The current user's profile details.
        """
        data = self._get("/me")
        return CurrentUser.model_validate(data)

    def get_top_artists(
        self,
        time_range: TimeRange | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Artist]:
        """Get the current user's top artists.

        Args:
            time_range: Over what time frame the affinities are computed.
                Valid values are `long_term`, `medium_term`, and `short_term`.
            limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50.
            offset: The index of the first item to return. Default: 0.

        Returns:
            A paginated list of the current user's top artists.

        Raises:
            ValueError: If time_range is invalid.
        """
        params = self._build_top_items_params(
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        data = self._get("/me/top/artists", params=params)
        return Page[Artist].model_validate(data)

    def get_top_tracks(
        self,
        time_range: TimeRange | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Track]:
        """Get the current user's top tracks.

        Args:
            time_range: Over what time frame the affinities are computed.
                Valid values are `long_term`, `medium_term`, and `short_term`.
            limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50.
            offset: The index of the first item to return. Default: 0.

        Returns:
            A paginated list of the current user's top tracks.

        Raises:
            ValueError: If time_range is invalid.
        """
        params = self._build_top_items_params(
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        data = self._get("/me/top/tracks", params=params)
        return Page[Track].model_validate(data)

    def follow_playlist(self, id: str, public: bool | None = None) -> None:
        """Add the current user as a follower of a playlist.

        Args:
            id: The Spotify ID of the playlist to follow.
            public: If `True`, the playlist is included in the current user's
                public playlists. If `False`, it remains private.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        payload = {"public": public} if public is not None else None
        self._put(f"/playlists/{id}/followers", json=payload)

    def unfollow_playlist(self, id: str) -> None:
        """Remove the current user as a follower of a playlist.

        Args:
            id: The Spotify ID of the playlist to unfollow.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        self._delete(f"/playlists/{id}/followers")

    def get_followed_artists(
        self, after: str | None = None, limit: int | None = None
    ) -> CursorPage[Artist]:
        """Get the current user's followed artists.

        Args:
            after: The last artist ID retrieved from the previous request.
            limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50.

        Returns:
            A cursor-paginated list of followed artists.
        """
        params: dict[str, str | int] = {"type": "artist"}
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit

        data = self._get("/me/following", params=params)
        return CursorPage[Artist].model_validate(data["artists"])

    def follow_artists_or_users(
        self, type_: FollowType, ids: list[str]
    ) -> None:
        """Add the current user as follower of one or more artists/users.

        Args:
            type_: Resource type to follow (`artist` or `user`).
            ids: Spotify IDs to follow.

        Raises:
            ValueError: If ids is empty or type_ is invalid.
        """
        params = self._build_follow_params(type_=type_, ids=ids)
        self._put("/me/following", params=params)

    def unfollow_artists_or_users(
        self, type_: FollowType, ids: list[str]
    ) -> None:
        """Remove artists/users from the current user's follows.

        Args:
            type_: Resource type to unfollow (`artist` or `user`).
            ids: Spotify IDs to unfollow.

        Raises:
            ValueError: If ids is empty or type_ is invalid.
        """
        params = self._build_follow_params(type_=type_, ids=ids)
        self._delete("/me/following", params=params)

    def check_follows_artists_or_users(
        self, type_: FollowType, ids: list[str]
    ) -> list[bool]:
        """Check if the current user follows artists/users.

        Args:
            type_: Resource type to check (`artist` or `user`).
            ids: Spotify IDs to check.

        Returns:
            A list of booleans aligned to input ids.

        Raises:
            ValueError: If ids is empty, type_ is invalid, or the response
                shape is not `list[bool]`.
        """
        params = self._build_follow_params(type_=type_, ids=ids)
        data = self._get("/me/following/contains", params=params)
        return self._validate_bool_list_response(
            data,
            endpoint="/me/following/contains",
        )

    def check_if_follows_playlist(
        self, id: str, user_ids: list[str]
    ) -> list[bool]:
        """Check if users follow a playlist.

        Args:
            id: The Spotify ID of the playlist.
            user_ids: Spotify user IDs to check.

        Returns:
            A list of booleans aligned to input user_ids.

        Raises:
            ValueError: If id is empty, user_ids is empty, or the response
                shape is not `list[bool]`.
        """
        if not id:
            raise ValueError("id cannot be empty")
        if not user_ids:
            raise ValueError("user_ids cannot be empty")

        data = self._get(
            f"/playlists/{id}/followers/contains",
            params={"ids": ",".join(user_ids)},
        )
        return self._validate_bool_list_response(
            data,
            endpoint=f"/playlists/{id}/followers/contains",
        )

    def _build_top_items_params(
        self,
        time_range: TimeRange | None,
        limit: int | None,
        offset: int | None,
    ) -> dict[str, str | int]:
        params: dict[str, str | int] = {}
        if time_range is not None:
            if time_range not in VALID_TIME_RANGES:
                raise ValueError(
                    f"Invalid time_range. Valid values: {VALID_TIME_RANGES}"
                )
            params["time_range"] = time_range
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params

    def _build_follow_params(
        self, type_: FollowType, ids: list[str]
    ) -> dict[str, str]:
        if type_ not in VALID_FOLLOW_TYPES:
            raise ValueError(
                f"Invalid type_. Valid values: {VALID_FOLLOW_TYPES}"
            )
        if not ids:
            raise ValueError("ids cannot be empty")
        return {"type": type_, "ids": ",".join(ids)}
