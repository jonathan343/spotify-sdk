"""Playlist models."""

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .base import SpotifyModel
from .common import (
    ExternalUrls,
    Image,
    Page,
)

if TYPE_CHECKING:
    from .track import Track


class PublicUser(SpotifyModel):
    """Public user profile for embedded user references."""

    external_urls: ExternalUrls
    href: str
    id: str
    type_: Literal["user"] = Field(alias="type")
    uri: str
    display_name: str | None = None


class PlaylistTracksRef(SpotifyModel):
    """Reference to playlist tracks with total count (used in SimplifiedPlaylist)."""

    href: str
    total: int


class PlaylistTrack(SpotifyModel):
    """Track item in a playlist with metadata about when/who added it."""

    added_at: datetime | None = None
    added_by: PublicUser | None = None
    is_local: bool
    track: "Track | None"


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
    tracks: PlaylistTracksRef
    type_: Literal["playlist"] = Field(alias="type")
    uri: str


class Playlist(SimplifiedPlaylist):
    """Complete playlist with tracks info."""

    tracks: Page["PlaylistTrack"]  # type: ignore[assignment]
