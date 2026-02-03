"""Audiobook and chapter models."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import SpotifyModel
from .common import Copyright, ExternalUrls, Image, Page, Restriction


class AudiobookAuthor(SpotifyModel):
    """Author of an audiobook."""

    name: str


class AudiobookNarrator(SpotifyModel):
    """Narrator of an audiobook."""

    name: str


class ResumePoint(SpotifyModel):
    """Resume point for a chapter."""

    fully_played: bool
    resume_position_ms: int


class SimplifiedAudiobook(SpotifyModel):
    """Basic audiobook info embedded in other objects."""

    authors: list[AudiobookAuthor]
    available_markets: list[str] | None = None
    copyrights: list[Copyright]
    description: str
    html_description: str
    edition: str | None = None
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    languages: list[str]
    media_type: str
    name: str
    narrators: list[AudiobookNarrator]
    publisher: str
    type_: Literal["audiobook"] = Field(alias="type")
    uri: str
    total_chapters: int


class SimplifiedChapter(SpotifyModel):
    """Basic chapter info embedded in other objects."""

    audio_preview_url: str | None
    available_markets: list[str] | None = None
    chapter_number: int
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    is_playable: bool | None = None
    languages: list[str]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restriction | None = None
    resume_point: ResumePoint | None = None
    type_: Literal["chapter"] = Field(alias="type")
    uri: str


class Audiobook(SimplifiedAudiobook):
    """Complete audiobook with chapter list."""

    chapters: Page[SimplifiedChapter]
