"""Show and episode models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from .audiobook import ResumePoint
from .base import SpotifyModel
from .common import Copyright, ExternalUrls, Image, Page, Restriction


class SimplifiedShow(SpotifyModel):
    """Basic show info embedded in other objects."""

    available_markets: list[str] | None = None
    copyrights: list[Copyright]
    description: str
    html_description: str
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    is_externally_hosted: bool | None = None
    languages: list[str]
    media_type: str
    name: str
    publisher: str
    type_: Literal["show"] = Field(alias="type")
    uri: str
    total_episodes: int


class SimplifiedEpisode(SpotifyModel):
    """Basic episode info embedded in other objects."""

    audio_preview_url: str | None = None
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    is_externally_hosted: bool | None = None
    is_playable: bool | None = None
    language: str | None = None
    languages: list[str]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restriction | None = None
    resume_point: ResumePoint | None = None
    type_: Literal["episode"] = Field(alias="type")
    uri: str


class Show(SimplifiedShow):
    """Complete show with episode list."""

    episodes: Page[SimplifiedEpisode]


class Episode(SimplifiedEpisode):
    """Complete episode with show info."""

    show: SimplifiedShow


class SavedShow(SpotifyModel):
    """Show saved in a user's library with timestamp metadata."""

    added_at: datetime
    show: SimplifiedShow
