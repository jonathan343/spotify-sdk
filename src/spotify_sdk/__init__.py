"""Spotify SDK - A Python client for the Spotify Web API."""

from importlib.metadata import version

from ._async._client import AsyncSpotifyClient
from ._sync._client import SpotifyClient
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SpotifyError,
)

__all__ = [
    # Clients
    "AsyncSpotifyClient",
    "SpotifyClient",
    # Exceptions
    "SpotifyError",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
]

__version__ = version("spotify-sdk")
