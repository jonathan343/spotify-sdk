"""Tests for the chapter service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Chapter

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
}

CHAPTER_RESPONSE = {
    "audio_preview_url": None,
    "available_markets": ["US"],
    "chapter_number": 1,
    "description": "Chapter description.",
    "html_description": "<p>Chapter description.</p>",
    "duration_ms": 600000,
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/chapter/456"},
    "href": "https://api.spotify.com/v1/chapters/456",
    "id": "456",
    "images": [
        {
            "url": "https://i.scdn.co/image/def",
            "height": 640,
            "width": 640,
        }
    ],
    "is_playable": True,
    "languages": ["en"],
    "name": "Chapter 1",
    "release_date": "2020-01-01",
    "release_date_precision": "day",
    "type": "chapter",
    "uri": "spotify:chapter:456",
    "audiobook": AUDIOBOOK_RESPONSE,
}


class TestChapterServiceGet:
    def test_get_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.chapters.get("")

    def test_get_chapter(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/chapters/456",
            json=CHAPTER_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            chapter = client.chapters.get("456")

        assert isinstance(chapter, Chapter)
        assert chapter.id == "456"
        assert chapter.name == "Chapter 1"
        assert chapter.audiobook.id == "123"

    def test_get_chapter_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/chapters/456?market=US",
            json=CHAPTER_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            chapter = client.chapters.get("456", market="US")

        assert chapter.id == "456"


class TestChapterServiceGetSeveral:
    def test_get_several_empty_list_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="ids cannot be empty"):
                client.chapters.get_several([])

    def test_get_several_chapters(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/chapters?ids=456%2C789",
            json={
                "chapters": [
                    CHAPTER_RESPONSE,
                    {**CHAPTER_RESPONSE, "id": "789", "name": "Chapter 2"},
                ]
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            chapters = client.chapters.get_several(["456", "789"])

        assert len(chapters) == 2
        assert all(isinstance(c, Chapter) for c in chapters)
        assert chapters[0].id == "456"
        assert chapters[1].id == "789"

    def test_get_several_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/chapters?ids=456&market=US",
            json={"chapters": [CHAPTER_RESPONSE]},
        )

        with SpotifyClient(access_token="test-token") as client:
            chapters = client.chapters.get_several(["456"], market="US")

        assert len(chapters) == 1
