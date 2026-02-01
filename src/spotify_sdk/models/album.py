"""Album models."""

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .artist import SimplifiedArtist
from .base import SpotifyModel
from .common import (
    Copyright,
    ExternalIds,
    ExternalUrls,
    Image,
    Page,
    Restriction,
)

if TYPE_CHECKING:
    from .track import SimplifiedTrack


class SimplifiedAlbum(SpotifyModel):
    """Basic album info embedded in other objects."""

    album_type: str
    total_tracks: int
    available_markets: list[str] | None = None
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restriction | None = None
    type_: Literal["album"] = Field(alias="type")
    uri: str
    artists: list[SimplifiedArtist]


class Album(SimplifiedAlbum):
    """Complete album with tracks, copyrights, and label info."""

    tracks: Page["SimplifiedTrack"]
    copyrights: list[Copyright]
    external_ids: ExternalIds
    label: str
    popularity: int
