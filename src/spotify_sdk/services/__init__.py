"""Service classes for Spotify API resources."""

from .albums import AlbumService
from .tracks import TrackService

__all__ = [
    "AlbumService",
    "TrackService",
]
