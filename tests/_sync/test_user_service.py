"""Tests for the user service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Artist, CurrentUser, CursorPage, Page, Track

CURRENT_USER_RESPONSE = {
    "country": "US",
    "display_name": "Test User",
    "email": "test@example.com",
    "explicit_content": {
        "filter_enabled": False,
        "filter_locked": False,
    },
    "external_urls": {"spotify": "https://open.spotify.com/user/test_user"},
    "followers": {"href": None, "total": 7},
    "href": "https://api.spotify.com/v1/users/test_user",
    "id": "test_user",
    "images": [
        {
            "url": "https://i.scdn.co/image/test-user",
            "height": 300,
            "width": 300,
        }
    ],
    "product": "premium",
    "type": "user",
    "uri": "spotify:user:test_user",
}

TOP_ARTIST_RESPONSE = {
    "external_urls": {"spotify": "https://open.spotify.com/artist/artist123"},
    "followers": {"href": None, "total": 1234},
    "genres": ["hip hop"],
    "href": "https://api.spotify.com/v1/artists/artist123",
    "id": "artist123",
    "images": [
        {
            "url": "https://i.scdn.co/image/artist123",
            "height": 640,
            "width": 640,
        }
    ],
    "name": "Test Artist",
    "popularity": 88,
    "type": "artist",
    "uri": "spotify:artist:artist123",
}

TOP_TRACK_RESPONSE = {
    "album": {
        "album_type": "album",
        "artists": [
            {
                "external_urls": {
                    "spotify": "https://open.spotify.com/artist/artist123"
                },
                "href": "https://api.spotify.com/v1/artists/artist123",
                "id": "artist123",
                "name": "Test Artist",
                "type": "artist",
                "uri": "spotify:artist:artist123",
            }
        ],
        "available_markets": ["US"],
        "external_urls": {
            "spotify": "https://open.spotify.com/album/album123"
        },
        "href": "https://api.spotify.com/v1/albums/album123",
        "id": "album123",
        "images": [],
        "name": "Test Album",
        "release_date": "2024-01-01",
        "release_date_precision": "day",
        "total_tracks": 10,
        "type": "album",
        "uri": "spotify:album:album123",
    },
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/artist123"
            },
            "href": "https://api.spotify.com/v1/artists/artist123",
            "id": "artist123",
            "name": "Test Artist",
            "type": "artist",
            "uri": "spotify:artist:artist123",
        }
    ],
    "available_markets": ["US"],
    "disc_number": 1,
    "duration_ms": 215000,
    "explicit": False,
    "external_ids": {"isrc": "USABC2400001"},
    "external_urls": {"spotify": "https://open.spotify.com/track/track123"},
    "href": "https://api.spotify.com/v1/tracks/track123",
    "id": "track123",
    "name": "Test Track",
    "popularity": 74,
    "preview_url": None,
    "track_number": 1,
    "type": "track",
    "uri": "spotify:track:track123",
    "is_local": False,
}


class TestUserServiceGetCurrentProfile:
    def test_get_current_profile(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me",
            json=CURRENT_USER_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            user = client.users.get_current_profile()

        assert isinstance(user, CurrentUser)
        assert user.id == "test_user"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"


class TestUserServiceGetTopArtists:
    def test_get_top_artists(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/top/artists",
            json={
                "href": "https://api.spotify.com/v1/me/top/artists",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [TOP_ARTIST_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.users.get_top_artists()

        assert isinstance(page, Page)
        assert page.total == 1
        assert isinstance(page.items[0], Artist)
        assert page.items[0].id == "artist123"

    def test_get_top_artists_with_filters(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/top/artists"
                "?time_range=short_term&limit=10&offset=5"
            ),
            json={
                "href": "https://api.spotify.com/v1/me/top/artists",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 1,
                "items": [TOP_ARTIST_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.users.get_top_artists(
                time_range="short_term",
                limit=10,
                offset=5,
            )

        assert page.limit == 10
        assert page.offset == 5

    def test_get_top_artists_invalid_time_range_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Invalid time_range"):
                client.users.get_top_artists(
                    time_range="invalid"  # type: ignore[arg-type]
                )


class TestUserServiceGetTopTracks:
    def test_get_top_tracks(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/top/tracks",
            json={
                "href": "https://api.spotify.com/v1/me/top/tracks",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [TOP_TRACK_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.users.get_top_tracks()

        assert isinstance(page, Page)
        assert page.total == 1
        assert isinstance(page.items[0], Track)
        assert page.items[0].id == "track123"


class TestUserServiceGetFollowedArtists:
    def test_get_followed_artists(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/following?type=artist",
            json={
                "artists": {
                    "href": "https://api.spotify.com/v1/me/following?type=artist",
                    "limit": 20,
                    "next": None,
                    "cursors": {"after": "artist123"},
                    "total": 1,
                    "items": [TOP_ARTIST_RESPONSE],
                }
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.users.get_followed_artists()

        assert isinstance(page, CursorPage)
        assert page.total == 1
        assert page.cursors.after == "artist123"
        assert isinstance(page.items[0], Artist)
        assert page.items[0].id == "artist123"

    def test_get_followed_artists_with_cursor_and_limit(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/following"
                "?type=artist&after=artist123&limit=10"
            ),
            json={
                "artists": {
                    "href": "https://api.spotify.com/v1/me/following?type=artist",
                    "limit": 10,
                    "next": None,
                    "cursors": {"after": "artist456"},
                    "total": 1,
                    "items": [TOP_ARTIST_RESPONSE],
                }
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.users.get_followed_artists(
                after="artist123",
                limit=10,
            )

        assert page.limit == 10
        assert page.cursors.after == "artist456"
