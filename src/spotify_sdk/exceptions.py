"""Exception classes for the Spotify SDK."""

from __future__ import annotations

from typing import Any


class SpotifyError(Exception):
    """Base exception for all Spotify SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class AuthenticationError(SpotifyError):
    """Invalid or expired authentication credentials."""

    pass


class BadRequestError(SpotifyError):
    """Invalid request parameters."""

    pass


class ForbiddenError(SpotifyError):
    """Insufficient permissions for this operation."""

    pass


class NotFoundError(SpotifyError):
    """Requested resource does not exist."""

    pass


class RateLimitError(SpotifyError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
        *,
        retry_after: int = 0,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self.retry_after = retry_after


class ServerError(SpotifyError):
    """Spotify API server error."""

    pass
