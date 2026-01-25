"""Spotify SDK - A Python client for the Spotify Web API."""

from .client import SpotifyClient
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
    # Client
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
