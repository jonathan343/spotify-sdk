"""Tests for the search service."""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.models import (
    Artist,
    Page,
    SearchResult,
    SimplifiedAlbum,
    Track,
)

SIMPLIFIED_ARTIST = {
    "external_urls": {"spotify": "https://open.spotify.com/artist/artist123"},
    "href": "https://api.spotify.com/v1/artists/artist123",
    "id": "artist123",
    "name": "Test Artist",
    "type": "artist",
    "uri": "spotify:artist:artist123",
}

SIMPLIFIED_ALBUM = {
    "album_type": "album",
    "total_tracks": 10,
    "available_markets": ["US"],
    "external_urls": {"spotify": "https://open.spotify.com/album/album123"},
    "href": "https://api.spotify.com/v1/albums/album123",
    "id": "album123",
    "images": [],
    "name": "Test Album",
    "release_date": "2024-01-01",
    "release_date_precision": "day",
    "type": "album",
    "uri": "spotify:album:album123",
    "artists": [SIMPLIFIED_ARTIST],
}

TRACK_RESPONSE = {
    "album": SIMPLIFIED_ALBUM,
    "artists": [SIMPLIFIED_ARTIST],
    "available_markets": ["US"],
    "disc_number": 1,
    "duration_ms": 180000,
    "explicit": False,
    "external_ids": {"isrc": "USAAA2400001"},
    "external_urls": {"spotify": "https://open.spotify.com/track/track123"},
    "href": "https://api.spotify.com/v1/tracks/track123",
    "id": "track123",
    "is_local": False,
    "name": "Test Track",
    "popularity": 72,
    "preview_url": None,
    "track_number": 1,
    "type": "track",
    "uri": "spotify:track:track123",
}

ARTIST_RESPONSE = {
    **SIMPLIFIED_ARTIST,
    "followers": {"href": None, "total": 1234},
    "genres": ["pop"],
    "images": [],
    "popularity": 80,
}


class TestSearchServiceSearch:
    @pytest.mark.anyio
    async def test_search_empty_query_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="q cannot be empty"):
                await client.search.search("", ["track"])

    @pytest.mark.anyio
    async def test_search_empty_types_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="types cannot be empty"):
                await client.search.search("test", [])

    @pytest.mark.anyio
    async def test_search_invalid_type_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Invalid types"):
                invalid_types: list[Any] = ["track", "invalid"]
                await client.search.search("test", invalid_types)

    @pytest.mark.anyio
    async def test_search_tracks_and_albums(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/search"
                "?q=remaster&type=track%2Calbum&limit=5&offset=0"
            ),
            json={
                "tracks": {
                    "href": "https://api.spotify.com/v1/search",
                    "limit": 5,
                    "next": None,
                    "offset": 0,
                    "previous": None,
                    "total": 1,
                    "items": [TRACK_RESPONSE],
                },
                "albums": {
                    "href": "https://api.spotify.com/v1/search",
                    "limit": 5,
                    "next": None,
                    "offset": 0,
                    "previous": None,
                    "total": 1,
                    "items": [SIMPLIFIED_ALBUM],
                },
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            result = await client.search.search("remaster", ["track", "album"])

        assert isinstance(result, SearchResult)
        assert isinstance(result.tracks, Page)
        assert isinstance(result.albums, Page)
        assert isinstance(result.tracks.items[0], Track)
        assert isinstance(result.albums.items[0], SimplifiedAlbum)
        assert result.tracks.items[0].id == "track123"
        assert result.albums.items[0].id == "album123"
        assert result.artists is None

    @pytest.mark.anyio
    async def test_search_with_all_optional_params(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/search"
                "?q=test&type=artist&limit=10&offset=5&market=US"
                "&include_external=audio"
            ),
            json={
                "artists": {
                    "href": "https://api.spotify.com/v1/search",
                    "limit": 10,
                    "next": None,
                    "offset": 5,
                    "previous": None,
                    "total": 1,
                    "items": [ARTIST_RESPONSE],
                }
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            result = await client.search.search(
                "test",
                ["artist"],
                market="US",
                limit=10,
                offset=5,
                include_external="audio",
            )

        assert isinstance(result.artists, Page)
        assert isinstance(result.artists.items[0], Artist)
        assert result.artists.items[0].id == "artist123"
