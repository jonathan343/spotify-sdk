"""Pydantic models for Spotify API responses."""

from .album import Album, SavedAlbum, SimplifiedAlbum
from .artist import Artist, SimplifiedArtist
from .audiobook import (
    Audiobook,
    AudiobookAuthor,
    AudiobookNarrator,
    Chapter,
    ResumePoint,
    SavedAudiobook,
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
from .player import (
    CurrentlyPlaying,
    PlaybackActions,
    PlaybackContext,
    PlaybackItem,
    PlaybackQueue,
    PlaybackState,
    PlayerDevice,
    RecentlyPlayedItem,
    RecentlyPlayedPage,
)
from .playlist import (
    Playlist,
    PlaylistTrack,
    PlaylistTracksRef,
    PublicUser,
    SimplifiedPlaylist,
)
from .search import SearchResult
from .show import (
    Episode,
    SavedEpisode,
    SavedShow,
    Show,
    SimplifiedEpisode,
    SimplifiedShow,
)
from .track import SavedTrack, SimplifiedTrack, Track
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
    # Player
    "CurrentlyPlaying",
    "PlaybackActions",
    "PlaybackContext",
    "PlaybackItem",
    "PlaybackQueue",
    "PlaybackState",
    "PlayerDevice",
    "RecentlyPlayedItem",
    "RecentlyPlayedPage",
    # Artist
    "Artist",
    "SimplifiedArtist",
    # Track
    "SavedTrack",
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
    "SavedAudiobook",
    "SimplifiedAudiobook",
    "SimplifiedChapter",
    # Playlist
    "Playlist",
    "PlaylistTrack",
    "PlaylistTracksRef",
    "PublicUser",
    "SimplifiedPlaylist",
    # Search
    "SearchResult",
    # Show
    "Episode",
    "SavedEpisode",
    "SavedShow",
    "Show",
    "SimplifiedEpisode",
    "SimplifiedShow",
]
