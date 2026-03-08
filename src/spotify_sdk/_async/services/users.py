"""User service for Spotify API."""

from __future__ import annotations

from typing import Literal, get_args

from ...models import Artist, CurrentUser, CursorPage, Page, Track
from .._base_service import AsyncBaseService

TimeRange = Literal["long_term", "medium_term", "short_term"]
VALID_TIME_RANGES = set(get_args(TimeRange))
FollowType = Literal["artist", "user"]
VALID_FOLLOW_TYPES = set(get_args(FollowType))


class AsyncUserService(AsyncBaseService):
    """Operations for Spotify users."""

    async def get_current_profile(self) -> CurrentUser:
        """Get detailed profile information about the current user.

        Returns:
            The current user's profile details.
        """
        data = await self._get("/me")
        return CurrentUser.model_validate(data)

    async def get_top_artists(
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
        data = await self._get("/me/top/artists", params=params)
        return Page[Artist].model_validate(data)

    async def get_top_tracks(
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
        data = await self._get("/me/top/tracks", params=params)
        return Page[Track].model_validate(data)

    async def get_followed_artists(
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

        data = await self._get("/me/following", params=params)
        return CursorPage[Artist].model_validate(data["artists"])

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
