"""Tests for the user service."""

import json

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


class TestUserServiceFollowPlaylist:
    def test_follow_playlist_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.users.follow_playlist("")

    def test_follow_playlist_defaults_to_public(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/playlists/playlist123/followers",
            method="PUT",
            status_code=204,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.users.follow_playlist("playlist123")

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "PUT"
        assert requests[0].content == b""

    def test_follow_playlist_private(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/playlists/playlist123/followers",
            method="PUT",
            status_code=204,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.users.follow_playlist("playlist123", public=False)

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "PUT"
        assert json.loads(requests[0].content.decode()) == {"public": False}


class TestUserServiceUnfollowPlaylist:
    def test_unfollow_playlist_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.users.unfollow_playlist("")

    def test_unfollow_playlist(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/playlists/playlist123/followers",
            method="DELETE",
            status_code=204,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.users.unfollow_playlist("playlist123")

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "DELETE"


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


class TestUserServiceFollowArtistsOrUsers:
    def test_follow_artists_or_users_empty_ids_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="ids cannot be empty"):
                client.users.follow_artists_or_users("artist", [])

    def test_follow_artists_or_users_invalid_type_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Invalid type_"):
                client.users.follow_artists_or_users(
                    "playlist",  # type: ignore[arg-type]
                    ["artist123"],
                )

    def test_follow_artists_or_users(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/following"
                "?type=artist&ids=artist123%2Cartist456"
            ),
            method="PUT",
            status_code=204,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.users.follow_artists_or_users(
                "artist", ["artist123", "artist456"]
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "PUT"
        assert requests[0].content == b""


class TestUserServiceUnfollowArtistsOrUsers:
    def test_unfollow_artists_or_users_empty_ids_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="ids cannot be empty"):
                client.users.unfollow_artists_or_users("user", [])

    def test_unfollow_artists_or_users_invalid_type_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Invalid type_"):
                client.users.unfollow_artists_or_users(
                    "album",  # type: ignore[arg-type]
                    ["user123"],
                )

    def test_unfollow_artists_or_users(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/following"
                "?type=user&ids=user123%2Cuser456"
            ),
            method="DELETE",
            status_code=204,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.users.unfollow_artists_or_users(
                "user", ["user123", "user456"]
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "DELETE"


class TestUserServiceCheckFollowsArtistsOrUsers:
    def test_check_follows_artists_or_users(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/following/contains"
                "?type=user&ids=user123%2Cuser456"
            ),
            json=[True, False],
        )

        with SpotifyClient(access_token="test-token") as client:
            result = client.users.check_follows_artists_or_users(
                "user", ["user123", "user456"]
            )

        assert result == [True, False]

    def test_check_follows_artists_or_users_empty_ids_raises_error(
        self,
    ):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="ids cannot be empty"):
                client.users.check_follows_artists_or_users("artist", [])


class TestUserServiceCheckIfFollowsPlaylist:
    def test_check_if_follows_playlist_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.users.check_if_follows_playlist("", ["user123"])

    def test_check_if_follows_playlist_empty_user_ids_raises_error(
        self,
    ):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="user_ids cannot be empty"):
                client.users.check_if_follows_playlist("playlist123", [])

    def test_check_if_follows_playlist(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/playlists/playlist123"
                "/followers/contains?ids=user123%2Cuser456"
            ),
            json=[True, False],
        )

        with SpotifyClient(access_token="test-token") as client:
            result = client.users.check_if_follows_playlist(
                "playlist123", ["user123", "user456"]
            )

        assert result == [True, False]
