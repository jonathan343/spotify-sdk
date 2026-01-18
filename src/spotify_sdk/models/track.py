from typing import Literal

from pydantic import Field

from .album import SimplifiedAlbum
from .artist import SimplifiedArtist
from .base import SpotifyModel
from .common import ExternalIds, ExternalUrls, LinkedFrom, Restriction


class SimplifiedTrack(SpotifyModel):
    """Basic track info embedded in other objects."""

    artists: list[SimplifiedArtist]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    is_playable: bool | None = None
    linked_from: LinkedFrom | None = None
    restrictions: Restriction | None = None
    name: str
    preview_url: str | None
    track_number: int
    type_: Literal["track"] = Field(alias="type")
    uri: str
    is_local: bool


class Track(SimplifiedTrack):
    """Complete track with album, popularity, and external IDs."""

    album: SimplifiedAlbum
    external_ids: ExternalIds
    popularity: int
