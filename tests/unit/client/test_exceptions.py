"""Tests for exception classes."""

import pytest

from spotify_sdk import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SpotifyError,
)


class TestSpotifyError:
    def test_basic_error(self):
        error = SpotifyError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response_body is None

    def test_error_with_status_code(self):
        error = SpotifyError("Not found", status_code=404)
        assert error.status_code == 404

    def test_error_with_response_body(self):
        body = {"error": {"message": "Not found"}}
        error = SpotifyError("Not found", status_code=404, response_body=body)
        assert error.response_body == body

    def test_error_is_exception(self):
        error = SpotifyError("test")
        assert isinstance(error, Exception)

    def test_exception_args(self):
        error = SpotifyError("test message")
        assert error.args == ("test message",)


class TestAuthenticationError:
    def test_inherits_from_spotify_error(self):
        error = AuthenticationError("Invalid token", status_code=401)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 401

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise AuthenticationError("Invalid token")


class TestBadRequestError:
    def test_inherits_from_spotify_error(self):
        error = BadRequestError("Invalid parameter", status_code=400)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 400

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise BadRequestError("Invalid parameter")


class TestForbiddenError:
    def test_inherits_from_spotify_error(self):
        error = ForbiddenError("Access denied", status_code=403)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 403

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise ForbiddenError("Access denied")


class TestNotFoundError:
    def test_inherits_from_spotify_error(self):
        error = NotFoundError("Album not found", status_code=404)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 404

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise NotFoundError("Album not found")


class TestRateLimitError:
    def test_inherits_from_spotify_error(self):
        error = RateLimitError("Rate limited", status_code=429, retry_after=30)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 429

    def test_retry_after_attribute(self):
        error = RateLimitError("Rate limited", retry_after=30)
        assert error.retry_after == 30

    def test_default_retry_after(self):
        error = RateLimitError("Rate limited")
        assert error.retry_after == 0

    def test_with_all_args(self):
        body = {"error": {"message": "Rate limited"}}
        error = RateLimitError(
            "Rate limited",
            status_code=429,
            response_body=body,
            retry_after=60,
        )
        assert error.message == "Rate limited"
        assert error.status_code == 429
        assert error.response_body == body
        assert error.retry_after == 60

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise RateLimitError("Rate limited", retry_after=30)


class TestServerError:
    def test_inherits_from_spotify_error(self):
        error = ServerError("Internal error", status_code=500)
        assert isinstance(error, SpotifyError)
        assert error.status_code == 500

    def test_catchable_as_spotify_error(self):
        with pytest.raises(SpotifyError):
            raise ServerError("Internal error")
