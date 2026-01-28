"""Tests for the track service."""

from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Track

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


class TestTrackServiceGet:
    def test_get_track(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/tracks/789",
            json=TRACK_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            track = client.tracks.get("789")

        assert isinstance(track, Track)
        assert track.id == "789"
        assert track.name == "Wesley's Theory"


class TestTrackServiceGetSeveral:
    def test_get_several_tracks(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://api.spotify.com/v1/tracks?ids=789%2C012",
            json={
                "tracks": [
                    TRACK_RESPONSE,
                    {
                        **TRACK_RESPONSE,
                        "id": "012",
                        "name": "For Free?",
                    },
                ]
            },
        )

        with SpotifyClient(access_token="test-token") as client:
            tracks = client.tracks.get_several(["789", "012"])

        assert len(tracks) == 2
        assert all(isinstance(t, Track) for t in tracks)
        assert tracks[0].id == "789"
        assert tracks[1].id == "012"
