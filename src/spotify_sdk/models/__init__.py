"""Pydantic models for Spotify API responses."""

from .album import Album, SavedAlbum, SimplifiedAlbum
from .artist import Artist, SimplifiedArtist
from .audiobook import (
    Audiobook,
    AudiobookAuthor,
    AudiobookNarrator,
    Chapter,
    ResumePoint,
    SimplifiedAudiobook,
    SimplifiedChapter,
)
from .common import (
    Copyright,
    Cursor,
    CursorPage,
    ExternalIds,
    ExternalUrls,
    Followers,
    Image,
    LinkedFrom,
    Page,
    Restriction,
)
from .playlist import (
    Playlist,
    PlaylistTrack,
    PlaylistTracksRef,
    PublicUser,
    SimplifiedPlaylist,
)
from .track import SimplifiedTrack, Track
from .user import CurrentUser, ExplicitContent

# Rebuild models that use forward references
Album.model_rebuild()
Playlist.model_rebuild()
PlaylistTrack.model_rebuild()

__all__ = [
    # Common
    "Copyright",
    "Cursor",
    "CursorPage",
    "ExternalIds",
    "ExternalUrls",
    "Followers",
    "Image",
    "LinkedFrom",
    "Page",
    "Restriction",
    # Artist
    "Artist",
    "SimplifiedArtist",
    # Track
    "SimplifiedTrack",
    "Track",
    # User
    "CurrentUser",
    "ExplicitContent",
    # Album
    "Album",
    "SavedAlbum",
    "SimplifiedAlbum",
    # Audiobook
    "Audiobook",
    "AudiobookAuthor",
    "AudiobookNarrator",
    "Chapter",
    "ResumePoint",
    "SimplifiedAudiobook",
    "SimplifiedChapter",
    # Playlist
    "Playlist",
    "PlaylistTrack",
    "PlaylistTracksRef",
    "PublicUser",
    "SimplifiedPlaylist",
]
