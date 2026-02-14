"""Tests for the show service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.models import Page, SavedShow, Show, SimplifiedEpisode

SIMPLIFIED_SHOW_RESPONSE = {
    "available_markets": ["US"],
    "copyrights": [
        {"text": "(C) 2024 Test Publisher", "type": "C"},
    ],
    "description": "Test show description.",
    "html_description": "<p>Test show description.</p>",
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/show/123"},
    "href": "https://api.spotify.com/v1/shows/123",
    "id": "123",
    "images": [
        {
            "url": "https://i.scdn.co/image/show",
            "height": 640,
            "width": 640,
        }
    ],
    "is_externally_hosted": False,
    "languages": ["en"],
    "media_type": "audio",
    "name": "Test Show",
    "publisher": "Test Publisher",
    "type": "show",
    "uri": "spotify:show:123",
    "total_episodes": 1,
}

EPISODE_RESPONSE = {
    "audio_preview_url": None,
    "description": "Episode description.",
    "html_description": "<p>Episode description.</p>",
    "duration_ms": 1800000,
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/episode/456"},
    "href": "https://api.spotify.com/v1/episodes/456",
    "id": "456",
    "images": [
        {
            "url": "https://i.scdn.co/image/episode",
            "height": 640,
            "width": 640,
        }
    ],
    "is_externally_hosted": False,
    "is_playable": True,
    "language": "en",
    "languages": ["en"],
    "name": "Episode 1",
    "release_date": "2024-01-01",
    "release_date_precision": "day",
    "type": "episode",
    "uri": "spotify:episode:456",
}

SHOW_RESPONSE = {
    **SIMPLIFIED_SHOW_RESPONSE,
    "episodes": {
        "href": "https://api.spotify.com/v1/shows/123/episodes",
        "limit": 20,
        "next": None,
        "offset": 0,
        "previous": None,
        "total": 1,
        "items": [EPISODE_RESPONSE],
    },
}

SAVED_SHOW_RESPONSE = {
    "added_at": "2024-01-15T12:34:56Z",
    "show": SIMPLIFIED_SHOW_RESPONSE,
}


class TestShowServiceGet:
    @pytest.mark.anyio
    async def test_get_empty_id_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                await client.shows.get("")

    @pytest.mark.anyio
    async def test_get_show(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/shows/123",
            json=SHOW_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            show = await client.shows.get("123")

        assert isinstance(show, Show)
        assert show.id == "123"
        assert show.name == "Test Show"
        assert show.episodes.items[0].name == "Episode 1"

    @pytest.mark.anyio
    async def test_get_show_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/shows/123?market=US",
            json=SHOW_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            show = await client.shows.get("123", market="US")

        assert show.id == "123"


class TestShowServiceGetEpisodes:
    @pytest.mark.anyio
    async def test_get_episodes_empty_id_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                await client.shows.get_episodes("")

    @pytest.mark.anyio
    async def test_get_episodes(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/shows/123/episodes?limit=20&offset=0",
            json={
                "href": "https://api.spotify.com/v1/shows/123/episodes",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [EPISODE_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.shows.get_episodes("123")

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SimplifiedEpisode)
        assert page.items[0].id == "456"

    @pytest.mark.anyio
    async def test_get_episodes_with_market_and_pagination(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/shows/123/episodes"
                "?market=US&limit=10&offset=5"
            ),
            json={
                "href": "https://api.spotify.com/v1/shows/123/episodes",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 20,
                "items": [EPISODE_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.shows.get_episodes(
                "123",
                market="US",
                limit=10,
                offset=5,
            )

        assert page.limit == 10
        assert page.offset == 5
        assert page.total == 20


class TestShowServiceGetSaved:
    @pytest.mark.anyio
    async def test_get_saved(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/shows?limit=20&offset=0",
            json={
                "href": "https://api.spotify.com/v1/me/shows",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [SAVED_SHOW_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.shows.get_saved()

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SavedShow)
        assert page.items[0].show.id == "123"

    @pytest.mark.anyio
    async def test_get_saved_with_pagination(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/shows?limit=10&offset=5",
            json={
                "href": "https://api.spotify.com/v1/me/shows",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 1,
                "items": [SAVED_SHOW_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.shows.get_saved(limit=10, offset=5)

        assert page.limit == 10
        assert page.offset == 5
