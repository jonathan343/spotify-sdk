"""Player and playback models."""

from __future__ import annotations

from datetime import datetime
from typing import TypeAlias

from pydantic import Field

from .base import SpotifyModel
from .common import Cursor, ExternalUrls
from .show import Episode
from .track import Track

PlaybackItem: TypeAlias = Track | Episode


class PlayerDevice(SpotifyModel):
    """A playback device available to the current user."""

    id: str | None = None
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type_: str = Field(alias="type")
    volume_percent: int | None = None
    supports_volume: bool | None = None


class PlaybackContext(SpotifyModel):
    """Context object for the current playback source."""

    type_: str = Field(alias="type")
    href: str | None = None
    external_urls: ExternalUrls
    uri: str


class PlaybackActions(SpotifyModel):
    """Player actions that are currently disallowed."""

    disallows: dict[str, bool] = Field(default_factory=dict)


class PlaybackState(SpotifyModel):
    """Current playback state for the active device."""

    device: PlayerDevice
    repeat_state: str
    shuffle_state: bool
    smart_shuffle: bool | None = None
    context: PlaybackContext | None = None
    timestamp: int
    progress_ms: int | None = None
    is_playing: bool
    item: PlaybackItem | None = None
    currently_playing_type: str | None = None
    actions: PlaybackActions | None = None


class CurrentlyPlaying(SpotifyModel):
    """Currently playing item without full device state."""

    context: PlaybackContext | None = None
    timestamp: int
    progress_ms: int | None = None
    is_playing: bool
    item: PlaybackItem | None = None
    currently_playing_type: str | None = None
    actions: PlaybackActions | None = None


class RecentlyPlayedItem(SpotifyModel):
    """A track from the user's recent playback history."""

    track: Track
    played_at: datetime
    context: PlaybackContext | None = None


class RecentlyPlayedPage(SpotifyModel):
    """Cursor-paginated recently played response."""

    href: str
    limit: int
    next: str | None
    cursors: Cursor
    items: list[RecentlyPlayedItem]


class PlaybackQueue(SpotifyModel):
    """Current playback queue for the user."""

    currently_playing: PlaybackItem | None = None
    queue: list[PlaybackItem]
