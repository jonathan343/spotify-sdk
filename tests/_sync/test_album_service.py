"""Tests for the album service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Album, Page, SimplifiedTrack

# Minimal album response for testing
ALBUM_RESPONSE = {
    "album_type": "album",
    "total_tracks": 16,
    "available_markets": ["US"],
    "external_urls": {"spotify": "https://open.spotify.com/album/123"},
    "href": "https://api.spotify.com/v1/albums/123",
    "id": "123",
    "images": [
        {
            "url": "https://i.scdn.co/image/abc",
            "height": 640,
            "width": 640,
        }
    ],
    "name": "To Pimp a Butterfly",
    "release_date": "2015-03-15",
    "release_date_precision": "day",
    "type": "album",
    "uri": "spotify:album:123",
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/456"
            },
            "href": "https://api.spotify.com/v1/artists/456",
            "id": "456",
            "name": "Kendrick Lamar",
            "type": "artist",
            "uri": "spotify:artist:456",
        }
    ],
    "tracks": {
        "href": "https://api.spotify.com/v1/albums/123/tracks",
        "limit": 50,
        "next": None,
        "offset": 0,
        "previous": None,
        "total": 16,
        "items": [],
    },
    "copyrights": [
        {"text": "(C) 2015 Test Records", "type": "C"},
    ],
    "external_ids": {"upc": "123456789"},
    "label": "Test Records",
    "popularity": 85,
}

TRACK_RESPONSE = {
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/456"
            },
            "href": "https://api.spotify.com/v1/artists/456",
            "id": "456",
            "name": "Kendrick Lamar",
            "type": "artist",
            "uri": "spotify:artist:456",
        }
    ],
    "available_markets": ["US"],
    "disc_number": 1,
    "duration_ms": 289000,
    "explicit": True,
    "external_urls": {"spotify": "https://open.spotify.com/track/789"},
    "href": "https://api.spotify.com/v1/tracks/789",
    "id": "789",
    "name": "Wesley's Theory",
    "preview_url": None,
    "track_number": 1,
    "type": "track",
    "uri": "spotify:track:789",
    "is_local": False,
}


class TestAlbumServiceGet:
    def test_get_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="album_id cannot be empty"):
                client.albums.get("")

    def test_get_album(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123",
            json=ALBUM_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            album = client.albums.get("123")

        assert isinstance(album, Album)
        assert album.id == "123"
        assert album.name == "To Pimp a Butterfly"
        assert album.artists[0].name == "Kendrick Lamar"

    def test_get_album_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123?market=US",
            json=ALBUM_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            album = client.albums.get("123", market="US")

        assert album.id == "123"


class TestAlbumServiceGetSeveral:
    def test_get_several_empty_list_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="album_ids cannot be empty"):
                client.albums.get_several([])

    def test_get_several_albums(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums?ids=123%2C456",
            json={"albums": [ALBUM_RESPONSE, {**ALBUM_RESPONSE, "id": "456"}]},
        )

        with SpotifyClient(access_token="test-token") as client:
            albums = client.albums.get_several(["123", "456"])

        assert len(albums) == 2
        assert all(isinstance(a, Album) for a in albums)
        assert albums[0].id == "123"
        assert albums[1].id == "456"

    def test_get_several_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums?ids=123&market=US",
            json={"albums": [ALBUM_RESPONSE]},
        )

        with SpotifyClient(access_token="test-token") as client:
            albums = client.albums.get_several(["123"], market="US")

        assert len(albums) == 1


class TestAlbumServiceGetTracks:
    def test_get_tracks_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="album_id cannot be empty"):
                client.albums.get_tracks("")

    def test_get_tracks(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123/tracks?limit=20&offset=0",
            json={
                "href": "https://api.spotify.com/v1/albums/123/tracks",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [TRACK_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.albums.get_tracks("123")

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SimplifiedTrack)
        assert page.items[0].name == "Wesley's Theory"

    def test_get_tracks_with_pagination(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/albums/123/tracks?limit=10&offset=5",
            json={
                "href": "https://api.spotify.com/v1/albums/123/tracks",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 16,
                "items": [TRACK_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.albums.get_tracks("123", limit=10, offset=5)

        assert page.limit == 10
        assert page.offset == 5
        assert page.total == 16
