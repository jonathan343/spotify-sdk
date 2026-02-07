"""User models."""

from .base import SpotifyModel
from .common import Followers, Image
from .playlist import PublicUser


class ExplicitContent(SpotifyModel):
    """Explicit content settings for a user account."""

    filter_enabled: bool | None = None
    filter_locked: bool | None = None


class CurrentUser(PublicUser):
    """Current user's private profile details."""

    country: str | None = None
    email: str | None = None
    explicit_content: ExplicitContent | None = None
    followers: Followers | None = None
    images: list[Image]
    product: str | None = None
