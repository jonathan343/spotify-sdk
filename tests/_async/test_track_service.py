"""Tests for the track service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.models import Page, SavedTrack, Track

TRACK_RESPONSE = {
    "album": {
        "album_type": "album",
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
        "external_urls": {"spotify": "https://open.spotify.com/album/abc"},
        "href": "https://api.spotify.com/v1/albums/abc",
        "id": "abc",
        "images": [],
        "name": "To Pimp a Butterfly",
        "release_date": "2015-03-15",
        "release_date_precision": "day",
        "total_tracks": 16,
        "type": "album",
        "uri": "spotify:album:abc",
    },
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
    "external_ids": {"isrc": "USUM71500001"},
    "external_urls": {"spotify": "https://open.spotify.com/track/789"},
    "href": "https://api.spotify.com/v1/tracks/789",
    "id": "789",
    "name": "Wesley's Theory",
    "popularity": 70,
    "preview_url": None,
    "track_number": 1,
    "type": "track",
    "uri": "spotify:track:789",
    "is_local": False,
}

SAVED_TRACK_RESPONSE = {
    "added_at": "2024-01-15T12:34:56Z",
    "track": TRACK_RESPONSE,
}


class TestTrackServiceGet:
    @pytest.mark.anyio
    async def test_get_track(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/tracks/789",
            json=TRACK_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            track = await client.tracks.get("789")

        assert isinstance(track, Track)
        assert track.id == "789"
        assert track.name == "Wesley's Theory"


class TestTrackServiceGetSaved:
    @pytest.mark.anyio
    async def test_get_saved(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/tracks?limit=20&offset=0",
            json={
                "href": "https://api.spotify.com/v1/me/tracks",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [SAVED_TRACK_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.tracks.get_saved()

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SavedTrack)
        assert page.items[0].track.id == "789"

    @pytest.mark.anyio
    async def test_get_saved_with_market_and_pagination(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/tracks"
                "?limit=10&offset=5&market=US"
            ),
            json={
                "href": "https://api.spotify.com/v1/me/tracks",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 1,
                "items": [SAVED_TRACK_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.tracks.get_saved(
                limit=10,
                offset=5,
                market="US",
            )

        assert page.limit == 10
        assert page.offset == 5
        assert page.items[0].track.id == "789"
