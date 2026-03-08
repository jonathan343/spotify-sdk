"""Tests for the player service."""

import json

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.models import (
    CurrentlyPlaying,
    Episode,
    PlaybackQueue,
    PlaybackState,
    PlayerDevice,
    RecentlyPlayedPage,
    Track,
)

DEVICE_RESPONSE = {
    "id": "device123",
    "is_active": True,
    "is_private_session": False,
    "is_restricted": False,
    "name": "MacBook Pro",
    "type": "Computer",
    "volume_percent": 72,
    "supports_volume": True,
}

PLAYBACK_CONTEXT_RESPONSE = {
    "type": "playlist",
    "href": "https://api.spotify.com/v1/playlists/playlist123",
    "external_urls": {
        "spotify": "https://open.spotify.com/playlist/playlist123"
    },
    "uri": "spotify:playlist:playlist123",
}

TRACK_RESPONSE = {
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
    "show": {
        "available_markets": ["US"],
        "copyrights": [
            {"text": "(C) 2024 Test Publisher", "type": "C"},
        ],
        "description": "Test show description.",
        "html_description": "<p>Test show description.</p>",
        "explicit": False,
        "external_urls": {"spotify": "https://open.spotify.com/show/show123"},
        "href": "https://api.spotify.com/v1/shows/show123",
        "id": "show123",
        "images": [],
        "is_externally_hosted": False,
        "languages": ["en"],
        "media_type": "audio",
        "name": "Test Show",
        "publisher": "Test Publisher",
        "type": "show",
        "uri": "spotify:show:show123",
        "total_episodes": 5,
    },
}

PLAYBACK_STATE_RESPONSE = {
    "device": DEVICE_RESPONSE,
    "repeat_state": "off",
    "shuffle_state": False,
    "smart_shuffle": False,
    "context": PLAYBACK_CONTEXT_RESPONSE,
    "timestamp": 1710000000000,
    "progress_ms": 120000,
    "is_playing": True,
    "item": TRACK_RESPONSE,
    "currently_playing_type": "track",
    "actions": {"disallows": {"pausing": False}},
}

CURRENTLY_PLAYING_RESPONSE = {
    "context": PLAYBACK_CONTEXT_RESPONSE,
    "timestamp": 1710000005000,
    "progress_ms": 45000,
    "is_playing": True,
    "item": EPISODE_RESPONSE,
    "currently_playing_type": "episode",
    "actions": {"disallows": {}},
}

RECENTLY_PLAYED_RESPONSE = {
    "href": "https://api.spotify.com/v1/me/player/recently-played?limit=1",
    "limit": 1,
    "next": None,
    "cursors": {
        "after": "1710000000000",
        "before": "1709999999000",
    },
    "items": [
        {
            "track": TRACK_RESPONSE,
            "played_at": "2024-03-09T10:00:00Z",
            "context": PLAYBACK_CONTEXT_RESPONSE,
        }
    ],
}

QUEUE_RESPONSE = {
    "currently_playing": TRACK_RESPONSE,
    "queue": [EPISODE_RESPONSE],
}


class TestPlayerServiceGetPlaybackState:
    @pytest.mark.anyio
    async def test_get_playback_state(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/player"
                "?market=US&additional_types=track%2Cepisode"
            ),
            json=PLAYBACK_STATE_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            playback = await client.player.get_playback_state(
                market="US",
                additional_types=["track", "episode"],
            )

        assert isinstance(playback, PlaybackState)
        assert playback is not None
        assert playback.device.name == "MacBook Pro"
        assert isinstance(playback.item, Track)
        assert playback.item.id == "track123"

    @pytest.mark.anyio
    async def test_get_playback_state_no_content(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/player",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            playback = await client.player.get_playback_state()

        assert playback is None

    @pytest.mark.anyio
    async def test_get_playback_state_empty_additional_types_raises_error(
        self,
    ):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="additional_types cannot be empty",
            ):
                await client.player.get_playback_state(
                    additional_types=[],
                )


class TestPlayerServiceTransferPlayback:
    @pytest.mark.anyio
    async def test_transfer_playback(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/me/player",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.transfer_playback("device123", play=True)

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert json.loads(requests[0].content.decode()) == {
            "device_ids": ["device123"],
            "play": True,
        }

    @pytest.mark.anyio
    async def test_transfer_playback_empty_device_id_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="device_id cannot be empty"):
                await client.player.transfer_playback("")


class TestPlayerServiceGetDevices:
    @pytest.mark.anyio
    async def test_get_devices(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/player/devices",
            json={"devices": [DEVICE_RESPONSE]},
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            devices = await client.player.get_devices()

        assert len(devices) == 1
        assert isinstance(devices[0], PlayerDevice)
        assert devices[0].id == "device123"


class TestPlayerServiceGetCurrentlyPlaying:
    @pytest.mark.anyio
    async def test_get_currently_playing(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/player/currently-playing"
                "?market=US&additional_types=episode"
            ),
            json=CURRENTLY_PLAYING_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            playing = await client.player.get_currently_playing(
                market="US",
                additional_types=["episode"],
            )

        assert isinstance(playing, CurrentlyPlaying)
        assert playing is not None
        assert isinstance(playing.item, Episode)
        assert playing.item.id == "456"

    @pytest.mark.anyio
    async def test_get_currently_playing_no_content(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/player/currently-playing",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            playing = await client.player.get_currently_playing()

        assert playing is None


class TestPlayerServiceStartPlayback:
    @pytest.mark.anyio
    async def test_start_playback_with_context(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/me/player/play?device_id=device123",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.start_playback(
                "device123",
                context_uri="spotify:playlist:playlist123",
                offset=2,
                position_ms=30000,
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert json.loads(requests[0].content.decode()) == {
            "context_uri": "spotify:playlist:playlist123",
            "offset": {"position": 2},
            "position_ms": 30000,
        }

    @pytest.mark.anyio
    async def test_start_playback_with_uris(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/me/player/play",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.start_playback(
                uris=[
                    "spotify:track:track123",
                    "spotify:episode:456",
                ],
                offset="spotify:episode:456",
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert json.loads(requests[0].content.decode()) == {
            "uris": [
                "spotify:track:track123",
                "spotify:episode:456",
            ],
            "offset": {"uri": "spotify:episode:456"},
        }

    @pytest.mark.anyio
    async def test_start_playback_conflicting_inputs_raise_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="context_uri and uris cannot both be provided",
            ):
                await client.player.start_playback(
                    context_uri="spotify:album:album123",
                    uris=["spotify:track:track123"],
                )

    @pytest.mark.anyio
    async def test_start_playback_offset_without_context_raises_error(
        self,
    ):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="offset requires context_uri or uris",
            ):
                await client.player.start_playback(offset=1)


class TestPlayerServicePlaybackControls:
    @pytest.mark.anyio
    async def test_pause_playback(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/player/pause"
                "?device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.pause_playback("device123")

    @pytest.mark.anyio
    async def test_skip_to_next(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.spotify.com/v1/me/player/next",
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.skip_to_next()

    @pytest.mark.anyio
    async def test_skip_to_previous(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=(
                "https://api.spotify.com/v1/me/player/previous"
                "?device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.skip_to_previous("device123")

    @pytest.mark.anyio
    async def test_seek(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/player/seek"
                "?position_ms=90000&device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.seek(90000, "device123")

    @pytest.mark.anyio
    async def test_set_repeat_mode(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/player/repeat"
                "?state=context&device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.set_repeat_mode("context", "device123")

    @pytest.mark.anyio
    async def test_set_volume(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/player/volume"
                "?volume_percent=65&device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.set_volume(65, "device123")

    @pytest.mark.anyio
    async def test_set_shuffle(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/player/shuffle"
                "?state=true&device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.set_shuffle(True, "device123")

    @pytest.mark.anyio
    async def test_set_volume_invalid_value_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="volume_percent must be between 0 and 100",
            ):
                await client.player.set_volume(101)


class TestPlayerServiceGetRecentlyPlayed:
    @pytest.mark.anyio
    async def test_get_recently_played(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=(
                "https://api.spotify.com/v1/me/player/recently-played"
                "?limit=1&after=1710000000000"
            ),
            json=RECENTLY_PLAYED_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            page = await client.player.get_recently_played(
                limit=1,
                after=1710000000000,
            )

        assert isinstance(page, RecentlyPlayedPage)
        assert len(page.items) == 1
        assert isinstance(page.items[0].track, Track)
        assert page.items[0].track.id == "track123"

    @pytest.mark.anyio
    async def test_get_recently_played_after_and_before_raise_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="after and before cannot both be provided",
            ):
                await client.player.get_recently_played(
                    after=1,
                    before=2,
                )


class TestPlayerServiceGetQueue:
    @pytest.mark.anyio
    async def test_get_queue(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/me/player/queue",
            json=QUEUE_RESPONSE,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            queue = await client.player.get_queue()

        assert isinstance(queue, PlaybackQueue)
        assert isinstance(queue.currently_playing, Track)
        assert isinstance(queue.queue[0], Episode)
        assert queue.queue[0].id == "456"


class TestPlayerServiceAddToQueue:
    @pytest.mark.anyio
    async def test_add_to_queue(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=(
                "https://api.spotify.com/v1/me/player/queue"
                "?uri=spotify%3Atrack%3Atrack123&device_id=device123"
            ),
            status_code=204,
        )

        async with AsyncSpotifyClient(access_token="test-token") as client:
            await client.player.add_to_queue(
                "spotify:track:track123",
                "device123",
            )

    @pytest.mark.anyio
    async def test_add_to_queue_empty_uri_raises_error(self):
        async with AsyncSpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="uri cannot be empty"):
                await client.player.add_to_queue("")
