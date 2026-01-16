from .base import SpotifyModel


class ExternalUrls(SpotifyModel):
    spotify: str


class Followers(SpotifyModel):
    href: str | None
    total: int


class Image(SpotifyModel):
    url: str
    height: int | None
    width: int | None
