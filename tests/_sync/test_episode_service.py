"""Tests for the episode service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Episode, Page, SavedEpisode

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
    "total_episodes": 10,
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
    "show": SIMPLIFIED_SHOW_RESPONSE,
}

SAVED_EPISODE_RESPONSE = {
    "added_at": "2024-01-15T12:34:56Z",
    "episode": EPISODE_RESPONSE,
}


class TestEpisodeServiceGet:
    def test_get_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.episodes.get("")

    def test_get_episode(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/episodes/456",
            json=EPISODE_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            episode = client.episodes.get("456")

        assert isinstance(episode, Episode)
        assert episode.id == "456"
        assert episode.name == "Episode 1"
        assert episode.show.id == "123"

    def test_get_episode_with_market(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/episodes/456?market=US",
            json=EPISODE_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            episode = client.episodes.get("456", market="US")

        assert episode.id == "456"


class TestEpisodeServiceGetSaved:
    def test_get_saved(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/episodes?limit=20&offset=0",
            json={
                "href": "https://api.spotify.com/v1/me/episodes",
                "limit": 20,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 1,
                "items": [SAVED_EPISODE_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.episodes.get_saved()

        assert isinstance(page, Page)
        assert page.total == 1
        assert len(page.items) == 1
        assert isinstance(page.items[0], SavedEpisode)
        assert page.items[0].episode.id == "456"

    def test_get_saved_with_market_and_pagination(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/episodes"
                "?limit=10&offset=5&market=US"
            ),
            json={
                "href": "https://api.spotify.com/v1/me/episodes",
                "limit": 10,
                "next": None,
                "offset": 5,
                "previous": None,
                "total": 1,
                "items": [SAVED_EPISODE_RESPONSE],
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            page = client.episodes.get_saved(
                limit=10,
                offset=5,
                market="US",
            )

        assert page.limit == 10
        assert page.offset == 5
