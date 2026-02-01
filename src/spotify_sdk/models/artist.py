"""Artist models."""

from typing import Literal

from pydantic import Field

from .base import SpotifyModel
from .common import ExternalUrls, Followers, Image


class SimplifiedArtist(SpotifyModel):
    """Basic artist info embedded in other objects."""

    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type_: Literal["artist"] = Field(alias="type")
    uri: str


class Artist(SimplifiedArtist):
    """Complete artist profile with followers, genres, and images."""

    followers: Followers
    genres: list[str]
    images: list[Image]
    popularity: int
