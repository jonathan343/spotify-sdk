"""Search models."""

from .album import SimplifiedAlbum
from .artist import Artist
from .audiobook import SimplifiedAudiobook
from .base import SpotifyModel
from .common import Page
from .playlist import SimplifiedPlaylist
from .show import SimplifiedEpisode, SimplifiedShow
from .track import Track


class SearchResult(SpotifyModel):
    """Typed container for Spotify search results."""

    tracks: Page[Track] | None = None
    artists: Page[Artist] | None = None
    albums: Page[SimplifiedAlbum] | None = None
    playlists: Page[SimplifiedPlaylist] | None = None
    shows: Page[SimplifiedShow] | None = None
    episodes: Page[SimplifiedEpisode] | None = None
    audiobooks: Page[SimplifiedAudiobook] | None = None
