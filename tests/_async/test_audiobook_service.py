"""Tests for the audiobook service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.models import Audiobook, Page, SimplifiedChapter

AUDIOBOOK_RESPONSE = {
    "authors": [{"name": "Test Author"}],
    "available_markets": ["US"],
    "copyrights": [{"text": "(C) 2020 Test Publisher", "type": "C"}],
    "description": "Test audiobook description.",
    "html_description": "<p>Test audiobook description.</p>",
    "edition": "Unabridged",
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/audiobook/123"},
    "href": "https://api.spotify.com/v1/audiobooks/123",
    "id": "123",
    "images": [
        {
            "url": "https://i.scdn.co/image/abc",
            "height": 640,
            "width": 640,
        }
    ],
    "languages": ["en"],
    "media_type": "audio",
    "name": "Test Audiobook",
    "narrators": [{"name": "Test Narrator"}],
    "publisher": "Test Publisher",
    "type": "audiobook",
    "uri": "spotify:audiobook:123",
    "total_chapters": 1,
    "chapters": {
        "href": "https://api.spotify.com/v1/audiobooks/123/chapters",
        "limit": 20,
        "next": None,
        "offset": 0,
        "previous": None,
        "total": 1,
        "items": [
            {
                "audio_preview_url": None,
                "available_markets": ["US"],
                "chapter_number": 1,
                "description": "Chapter description.",
                "html_description": "<p>Chapter description.</p>",
                "duration_ms": 600000,
                "explicit": False,
                "external_urls": {
                    "spotify": "https://open.spotify.com/episode/456"
                },
                "href": "https://api.spotify.com/v1/chapters/456",
                "id": "456",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/def",
                        "height": 640,
                        "width": 640,
                    }
                ],
                "languages": ["en"],
                "name": "Chapter 1",
                "release_date": "2020-01-01",
                "release_date_precision": "day",
                "type": "chapter",
                "uri": "spotify:episode:456",
            }
        ],
    },
}

CHAPTER_RESPONSE = {
    "audio_preview_url": None,
    "available_markets": ["US"],
    "chapter_number": 1,
    "description": "Chapter description.",
    "html_description": "<p>Chapter description.</p>",
    "duration_ms": 600000,
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/episode/456"},
    "href": "https://api.spotify.com/v1/chapters/456",
    "id": "456",
    "images": [
        {
            "url": "https://i.scdn.co/image/def",
            "height": 640,
            "width": 640,
        }
    ],
    "languages": ["en"],
    "name": "Chapter 1",
    "release_date": "2020-01-01",
    "release_date_precision": "day",
    "type": "chapter",
    "uri": "spotify:episode:456",
}


class TestAudiobookServiceGet:
    @pytest.mark.anyio
    async def test_get_empty_id_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                await client.audiobooks.get("")

    @pytest.mark.anyio
    async def test_get_audiobook(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/audiobooks/123",
            json=AUDIOBOOK_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            audiobook = await client.audiobooks.get("123")

        assert isinstance(audiobook, Audiobook)
        assert audiobook.id == "123"
        assert audiobook.name == "Test Audiobook"
        assert audiobook.authors[0].name == "Test Author"

    @pytest.mark.anyio
    async def test_get_audiobook_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/audiobooks/123?market=US",
            json=AUDIOBOOK_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            audiobook = await client.audiobooks.get("123", market="US")

        assert audiobook.id == "123"


class TestAudiobookServiceGetSeveral:
    @pytest.mark.anyio
    async def test_get_several_empty_list_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="ids cannot be empty"):
                await client.audiobooks.get_several([])

    @pytest.mark.anyio
    async def test_get_several_audiobooks(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/audiobooks?ids=123%2C456",
            json={
                "audiobooks": [
                    AUDIOBOOK_RESPONSE,
                    {**AUDIOBOOK_RESPONSE, "id": "456", "name": "Other Book"},
                ]
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            audiobooks = await client.audiobooks.get_several(["123", "456"])

        assert len(audiobooks) == 2
        assert all(isinstance(a, Audiobook) for a in audiobooks)
        assert audiobooks[0].id == "123"
        assert audiobooks[1].id == "456"

    @pytest.mark.anyio
    async def test_get_several_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/audiobooks?ids=123&market=US",
            json={"audiobooks": [AUDIOBOOK_RESPONSE]},
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            audiobooks = await client.audiobooks.get_several(
                ["123"], market="US"
            )

        assert len(audiobooks) == 1


class TestAudiobookServiceGetChapters:
    @pytest.mark.anyio
    async def test_get_chapters_empty_id_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                await client.audiobooks.get_chapters("")

    @pytest.mark.anyio
    async def test_get_chapters(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/audiobooks/123/chapters"
                "?limit=20&offset=0"
            ),
            json={
                "href": "https://api.spotify.com/v1/audiobooks/123/chapters",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [CHAPTER_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.audiobooks.get_chapters("123")

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SimplifiedChapter)
        assert page.items[0].name == "Chapter 1"

    @pytest.mark.anyio
    async def test_get_chapters_with_pagination(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/audiobooks/123/chapters"
                "?limit=10&offset=5"
            ),
            json={
                "href": "https://api.spotify.com/v1/audiobooks/123/chapters",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 20,
                "items": [CHAPTER_RESPONSE],
            },
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.audiobooks.get_chapters(
                "123", limit=10, offset=5
            )

        assert page.limit == 10
        assert page.offset == 5
        assert page.total == 20
