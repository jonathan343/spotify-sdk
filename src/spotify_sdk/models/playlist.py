"""Playlist models."""

from datetime import datetime
from typing import Literal, TypeAlias

from pydantic import Field

from .base import SpotifyModel
from .common import (
    ExternalUrls,
    Image,
    Page,
)
from .player import PlaybackItem


class PublicUser(SpotifyModel):
    """Public user profile for embedded user references."""

    external_urls: ExternalUrls
    href: str
    id: str
    type_: Literal["user"] = Field(alias="type")
    uri: str
    display_name: str | None = None


class PlaylistItemsRef(SpotifyModel):
    """Reference to playlist items with total count."""

    href: str
    total: int


class PlaylistItem(SpotifyModel):
    """Playlist item with metadata about when and who added it."""

    added_at: datetime | None = None
    added_by: PublicUser | None = None
    is_local: bool
    item: "PlaylistItemContent | None"


class PlaylistEpisode(SpotifyModel):
    """Episode payload returned by playlist items for some Spotify responses."""

    preview_url: str | None = None
    available_markets: list[str] | None = None
    explicit: bool
    type_: Literal["episode"] = Field(alias="type")
    episode: bool | None = None
    track_: bool | None = Field(alias="track", default=None)
    album: dict[str, object] | None = None
    artists: list[dict[str, object]] | None = None
    disc_number: int | None = None
    track_number: int | None = None
    duration_ms: int
    external_ids: dict[str, str] | None = None
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    popularity: int | None = None
    uri: str
    is_local: bool


PlaylistItemContent: TypeAlias = PlaybackItem | PlaylistEpisode


class SimplifiedPlaylist(SpotifyModel):
    """Basic playlist info embedded in other objects."""

    collaborative: bool
    description: str | None
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    name: str
    owner: PublicUser
    public: bool | None
    snapshot_id: str
    items: PlaylistItemsRef
    type_: Literal["playlist"] = Field(alias="type")
    uri: str


class Playlist(SimplifiedPlaylist):
    """Complete playlist with item details."""

    items: Page["PlaylistItem"]  # type: ignore[assignment]
