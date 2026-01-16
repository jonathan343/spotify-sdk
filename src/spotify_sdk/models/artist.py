from typing import Literal

from pydantic import Field

from .base import SpotifyModel
from .common import ExternalUrls, Followers, Image


class Artist(SpotifyModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type_: Literal["artist"] = Field(alias="type")
    uri: str
    # Full artist object fields (not present in simplified artist)
    followers: Followers | None = None
    genres: list[str] | None = None
    images: list[Image] | None = None
    popularity: int | None = Field(default=None, ge=0, le=100)
