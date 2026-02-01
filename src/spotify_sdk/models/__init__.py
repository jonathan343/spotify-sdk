"""Pydantic models for Spotify API responses."""

from .album import Album, SimplifiedAlbum
from .artist import Artist, SimplifiedArtist
from .common import (
    Copyright,
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

# Rebuild models that use forward references
Album.model_rebuild()
Playlist.model_rebuild()
PlaylistTrack.model_rebuild()

__all__ = [
    # Common
    "Copyright",
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
    # Album
    "Album",
    "SimplifiedAlbum",
    # Playlist
    "Playlist",
    "PlaylistTrack",
    "PlaylistTracksRef",
    "PublicUser",
    "SimplifiedPlaylist",
]
