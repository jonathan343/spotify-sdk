"""Common models shared across resources."""

from typing import Generic, Literal, TypeVar

from pydantic import Field

from .base import SpotifyModel

T = TypeVar("T")


class ExternalUrls(SpotifyModel):
    """URLs for opening a resource in the Spotify web player."""

    spotify: str


class Followers(SpotifyModel):
    """Follower information for an artist or playlist."""

    href: str | None
    total: int


class Image(SpotifyModel):
    """Cover art or profile image. Dimensions may be null for user-uploaded images."""

    url: str
    height: int | None
    width: int | None


class Restriction(SpotifyModel):
    """Content restriction. Reason is 'market', 'product', or 'explicit'."""

    reason: str


class Copyright(SpotifyModel):
    """Copyright statement. Type is 'C' (copyright) or 'P' (performance)."""

    text: str
    type_: str = Field(alias="type")


class ExternalIds(SpotifyModel):
    """External identifiers: ISRC for tracks, EAN or UPC for albums."""

    isrc: str | None = None
    ean: str | None = None
    upc: str | None = None


class LinkedFrom(SpotifyModel):
    """Original track info when track relinking has replaced the requested track."""

    external_urls: ExternalUrls
    href: str
    id: str
    type_: Literal["track"] = Field(alias="type")
    uri: str


class Page(SpotifyModel, Generic[T]):
    """Paginated response containing items and navigation links."""

    href: str
    limit: int
    next: str | None
    offset: int
    previous: str | None
    total: int
    items: list[T]
