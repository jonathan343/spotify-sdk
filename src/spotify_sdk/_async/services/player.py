"""Player service for Spotify API."""

from __future__ import annotations

from typing import Literal

from pydantic import TypeAdapter

from ...models import (
    CurrentlyPlaying,
    PlaybackQueue,
    PlaybackState,
    PlayerDevice,
    RecentlyPlayedPage,
)
from .._base_service import AsyncBaseService

_DEVICE_LIST_ADAPTER = TypeAdapter(list[PlayerDevice])
_ADDITIONAL_TYPES = {"track", "episode"}
_REPEAT_STATES = {"context", "off", "track"}


class AsyncPlayerService(AsyncBaseService):
    """Playback control and player state operations."""

    async def get_playback_state(
        self,
        market: str | None = None,
        additional_types: list[Literal["track", "episode"]] | None = None,
    ) -> PlaybackState | None:
        """Get the current user's playback state.

        Args:
            market: An ISO 3166-1 alpha-2 country code.
            additional_types: Additional item types to consider in playback.

        Returns:
            The current playback state, or `None` if nothing is active.
        """
        params = self._build_playback_lookup_params(
            market=market,
            additional_types=additional_types,
        )
        data = await self._get("/me/player", params=params)
        if not data:
            return None
        return PlaybackState.model_validate(data)

    async def transfer_playback(
        self,
        device_id: str,
        play: bool | None = None,
    ) -> None:
        """Transfer playback to another device.

        Args:
            device_id: The target Spotify Connect device ID.
            play: Whether playback should start immediately after transfer.

        Raises:
            ValueError: If `device_id` is empty.
        """
        self._validate_non_empty_string(device_id, field_name="device_id")

        payload: dict[str, list[str] | bool] = {"device_ids": [device_id]}
        if play is not None:
            payload["play"] = play
        await self._put("/me/player", json=payload)

    async def get_devices(self) -> list[PlayerDevice]:
        """Get the user's available playback devices."""
        data = await self._get("/me/player/devices")
        devices = data.get("devices")
        if not isinstance(devices, list):
            raise ValueError("Expected list response from /me/player/devices")
        return _DEVICE_LIST_ADAPTER.validate_python(devices)

    async def get_currently_playing(
        self,
        market: str | None = None,
        additional_types: list[Literal["track", "episode"]] | None = None,
    ) -> CurrentlyPlaying | None:
        """Get the item currently playing on the user's active device.

        Args:
            market: An ISO 3166-1 alpha-2 country code.
            additional_types: Additional item types to consider in playback.

        Returns:
            The current item, or `None` if nothing is active.
        """
        params = self._build_playback_lookup_params(
            market=market,
            additional_types=additional_types,
        )
        data = await self._get("/me/player/currently-playing", params=params)
        if not data:
            return None
        return CurrentlyPlaying.model_validate(data)

    async def start_playback(
        self,
        device_id: str | None = None,
        *,
        context_uri: str | None = None,
        uris: list[str] | None = None,
        offset: int | str | None = None,
        position_ms: int | None = None,
    ) -> None:
        """Start or resume playback on the user's active device.

        Args:
            device_id: Optional Spotify Connect device ID.
            context_uri: Context URI for an album, artist, or playlist.
            uris: Explicit track or episode URIs to play.
            offset: Starting offset as a zero-based position or item URI.
            position_ms: Position in milliseconds to start playback.

        Raises:
            ValueError: If parameters are empty, conflicting, or invalid.
        """
        self._validate_optional_device_id(device_id)

        if context_uri is not None and uris is not None:
            raise ValueError("context_uri and uris cannot both be provided")
        if context_uri is not None:
            self._validate_non_empty_string(
                context_uri,
                field_name="context_uri",
            )
        if uris is not None:
            self._validate_uri_list(uris)
        if offset is not None and context_uri is None and uris is None:
            raise ValueError("offset requires context_uri or uris")
        if position_ms is not None and position_ms < 0:
            raise ValueError("position_ms must be greater than or equal to 0")

        payload: dict[str, object] = {}
        if context_uri is not None:
            payload["context_uri"] = context_uri
        if uris is not None:
            payload["uris"] = uris
        if offset is not None:
            payload["offset"] = self._build_offset_payload(offset)
        if position_ms is not None:
            payload["position_ms"] = position_ms

        params = self._build_device_params(device_id)
        if payload:
            await self._put("/me/player/play", json=payload, params=params)
            return
        await self._put("/me/player/play", params=params)

    async def pause_playback(self, device_id: str | None = None) -> None:
        """Pause playback on the user's active device."""
        self._validate_optional_device_id(device_id)
        await self._put(
            "/me/player/pause",
            params=self._build_device_params(device_id),
        )

    async def skip_to_next(self, device_id: str | None = None) -> None:
        """Skip to the next item in the playback queue."""
        self._validate_optional_device_id(device_id)
        await self._post(
            "/me/player/next",
            params=self._build_device_params(device_id),
        )

    async def skip_to_previous(self, device_id: str | None = None) -> None:
        """Skip to the previous item in the playback queue."""
        self._validate_optional_device_id(device_id)
        await self._post(
            "/me/player/previous",
            params=self._build_device_params(device_id),
        )

    async def seek(
        self,
        position_ms: int,
        device_id: str | None = None,
    ) -> None:
        """Seek to a position within the currently playing item."""
        if position_ms < 0:
            raise ValueError("position_ms must be greater than or equal to 0")
        self._validate_optional_device_id(device_id)

        params = {
            "position_ms": position_ms,
            **self._build_device_params(device_id),
        }
        await self._put("/me/player/seek", params=params)

    async def set_repeat_mode(
        self,
        state: Literal["track", "context", "off"],
        device_id: str | None = None,
    ) -> None:
        """Set the repeat mode for the user's playback."""
        if state not in _REPEAT_STATES:
            raise ValueError("state must be one of: context, off, track")
        self._validate_optional_device_id(device_id)

        params = {"state": state, **self._build_device_params(device_id)}
        await self._put("/me/player/repeat", params=params)

    async def set_volume(
        self,
        volume_percent: int,
        device_id: str | None = None,
    ) -> None:
        """Set the volume for the user's playback device."""
        if not 0 <= volume_percent <= 100:
            raise ValueError("volume_percent must be between 0 and 100")
        self._validate_optional_device_id(device_id)

        params = {
            "volume_percent": volume_percent,
            **self._build_device_params(device_id),
        }
        await self._put("/me/player/volume", params=params)

    async def set_shuffle(
        self,
        state: bool,
        device_id: str | None = None,
    ) -> None:
        """Enable or disable shuffle for the user's playback."""
        self._validate_optional_device_id(device_id)

        params = {
            "state": str(state).lower(),
            **self._build_device_params(device_id),
        }
        await self._put("/me/player/shuffle", params=params)

    async def get_recently_played(
        self,
        limit: int | None = None,
        after: int | None = None,
        before: int | None = None,
    ) -> RecentlyPlayedPage:
        """Get the current user's recently played tracks.

        Args:
            limit: Maximum number of items to return (1-50).
            after: Unix timestamp in milliseconds. Returns items after this.
            before: Unix timestamp in milliseconds. Returns items before this.

        Raises:
            ValueError: If pagination values are invalid.
        """
        if limit is not None and not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        if after is not None and after < 0:
            raise ValueError("after must be greater than or equal to 0")
        if before is not None and before < 0:
            raise ValueError("before must be greater than or equal to 0")
        if after is not None and before is not None:
            raise ValueError("after and before cannot both be provided")

        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        data = await self._get("/me/player/recently-played", params=params)
        return RecentlyPlayedPage.model_validate(data)

    async def get_queue(self) -> PlaybackQueue:
        """Get the current user's playback queue."""
        data = await self._get("/me/player/queue")
        return PlaybackQueue.model_validate(data)

    async def add_to_queue(
        self,
        uri: str,
        device_id: str | None = None,
    ) -> None:
        """Add an item to the end of the user's playback queue."""
        self._validate_non_empty_string(uri, field_name="uri")
        self._validate_optional_device_id(device_id)

        params = {"uri": uri, **self._build_device_params(device_id)}
        await self._post("/me/player/queue", params=params)

    def _build_playback_lookup_params(
        self,
        *,
        market: str | None,
        additional_types: list[Literal["track", "episode"]] | None,
    ) -> dict[str, str]:
        params: dict[str, str] = {}
        if market is not None:
            params["market"] = market
        if additional_types is not None:
            params["additional_types"] = self._serialize_additional_types(
                additional_types
            )
        return params

    def _serialize_additional_types(
        self,
        additional_types: list[Literal["track", "episode"]],
    ) -> str:
        if not additional_types:
            raise ValueError("additional_types cannot be empty")

        invalid_types = sorted(
            value
            for value in additional_types
            if value not in _ADDITIONAL_TYPES
        )
        if invalid_types:
            raise ValueError(
                "additional_types must only contain 'track' or 'episode'"
            )
        return ",".join(additional_types)

    def _build_device_params(
        self,
        device_id: str | None,
    ) -> dict[str, str]:
        if device_id is None:
            return {}
        return {"device_id": device_id}

    def _build_offset_payload(self, offset: int | str) -> dict[str, int | str]:
        if isinstance(offset, int):
            if offset < 0:
                raise ValueError(
                    "offset position must be greater than or equal to 0"
                )
            return {"position": offset}

        self._validate_non_empty_string(offset, field_name="offset")
        return {"uri": offset}

    def _validate_optional_device_id(self, device_id: str | None) -> None:
        if device_id is not None:
            self._validate_non_empty_string(
                device_id,
                field_name="device_id",
            )

    def _validate_uri_list(self, uris: list[str]) -> None:
        if not uris:
            raise ValueError("uris cannot be empty")
        if any(not uri for uri in uris):
            raise ValueError("uris cannot contain empty values")

    def _validate_non_empty_string(
        self,
        value: str,
        *,
        field_name: str,
    ) -> None:
        if not value:
            raise ValueError(f"{field_name} cannot be empty")
