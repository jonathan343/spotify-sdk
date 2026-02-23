"""Tests for the playlist service."""

import json

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient
from spotify_sdk.models import Image, SimplifiedPlaylist

SIMPLIFIED_PLAYLIST_RESPONSE = {
    "collaborative": False,
    "description": "Test playlist description",
    "external_urls": {
        "spotify": "https://open.spotify.com/playlist/playlist123"
    },
    "href": "https://api.spotify.com/v1/playlists/playlist123",
    "id": "playlist123",
    "images": [
        {
            "url": "https://i.scdn.co/image/playlist123",
            "height": 640,
            "width": 640,
        }
    ],
    "name": "Test Playlist",
    "owner": {
        "external_urls": {
            "spotify": "https://open.spotify.com/user/test_user"
        },
        "href": "https://api.spotify.com/v1/users/test_user",
        "id": "test_user",
        "type": "user",
        "uri": "spotify:user:test_user",
        "display_name": "Test User",
    },
    "public": False,
    "snapshot_id": "snapshot-123",
    "tracks": {
        "href": "https://api.spotify.com/v1/playlists/playlist123/tracks",
        "total": 0,
    },
    "type": "playlist",
    "uri": "spotify:playlist:playlist123",
}

SNAPSHOT_RESPONSE = {"snapshot_id": "snapshot-456"}
IMAGE_RESPONSE = [
    {
        "url": "https://i.scdn.co/image/playlist-cover",
        "height": 640,
        "width": 640,
    }
]


class TestPlaylistServiceCreate:
    def test_create_playlist(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.spotify.com/v1/users/test_user/playlists",
            json=SIMPLIFIED_PLAYLIST_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            playlist = client.playlists.create(
                "test_user",
                "Test Playlist",
                public=False,
                collaborative=True,
                description="Test playlist description",
            )

        assert isinstance(playlist, SimplifiedPlaylist)
        assert playlist.id == "playlist123"
        assert playlist.name == "Test Playlist"
        assert playlist.snapshot_id == "snapshot-123"

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert json.loads(requests[0].content.decode()) == {
            "name": "Test Playlist",
            "public": False,
            "collaborative": True,
            "description": "Test playlist description",
        }

    def test_create_playlist_empty_user_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="user_id cannot be empty"):
                client.playlists.create("", "Test Playlist")

    def test_create_playlist_empty_name_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="name cannot be empty"):
                client.playlists.create("test_user", "")

    def test_create_playlist_collaborative_requires_private(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="public must be False when collaborative is True",
            ):
                client.playlists.create(
                    "test_user",
                    "Test Playlist",
                    collaborative=True,
                )


class TestPlaylistServiceChangeDetails:
    def test_change_details(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/playlists/playlist123",
            status_code=200,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.playlists.change_details(
                "playlist123",
                name="Updated Playlist",
                public=False,
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].method == "PUT"
        assert json.loads(requests[0].content.decode()) == {
            "name": "Updated Playlist",
            "public": False,
        }

    def test_change_details_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.change_details("", name="Updated")

    def test_change_details_no_fields_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="At least one field must be provided",
            ):
                client.playlists.change_details("playlist123")

    def test_change_details_public_and_collaborative_true_raises_error(
        self,
    ):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="public and collaborative cannot both be True",
            ):
                client.playlists.change_details(
                    "playlist123",
                    public=True,
                    collaborative=True,
                )


class TestPlaylistServiceReorderOrReplaceItems:
    def test_replace_items(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/playlists/playlist123/tracks",
            json=SNAPSHOT_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            snapshot_id = client.playlists.reorder_or_replace_items(
                "playlist123",
                uris=[
                    "spotify:track:track123",
                    "spotify:episode:episode456",
                ],
            )

        assert snapshot_id == "snapshot-456"
        requests = httpx_mock.get_requests()
        assert json.loads(requests[0].content.decode()) == {
            "uris": [
                "spotify:track:track123",
                "spotify:episode:episode456",
            ]
        }

    def test_reorder_items(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/playlists/playlist123/tracks",
            json=SNAPSHOT_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            snapshot_id = client.playlists.reorder_or_replace_items(
                "playlist123",
                range_start=1,
                insert_before=5,
                range_length=2,
                snapshot_id="snapshot-123",
            )

        assert snapshot_id == "snapshot-456"
        requests = httpx_mock.get_requests()
        assert json.loads(requests[0].content.decode()) == {
            "range_start": 1,
            "insert_before": 5,
            "range_length": 2,
            "snapshot_id": "snapshot-123",
        }

    def test_reorder_or_replace_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.reorder_or_replace_items(
                    "",
                    uris=["spotify:track:track123"],
                )

    def test_reorder_or_replace_mixed_modes_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="Replace mode cannot include reorder parameters",
            ):
                client.playlists.reorder_or_replace_items(
                    "playlist123",
                    uris=["spotify:track:track123"],
                    range_start=0,
                    insert_before=1,
                )

    def test_reorder_or_replace_missing_reorder_params_raises_error(
        self,
    ):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="range_start and insert_before are required for reorder",
            ):
                client.playlists.reorder_or_replace_items("playlist123")


class TestPlaylistServiceAddItems:
    def test_add_items(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.spotify.com/v1/playlists/playlist123/tracks",
            json=SNAPSHOT_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            snapshot_id = client.playlists.add_items(
                "playlist123",
                ["spotify:track:track123", "spotify:episode:episode456"],
                position=3,
            )

        assert snapshot_id == "snapshot-456"
        requests = httpx_mock.get_requests()
        assert json.loads(requests[0].content.decode()) == {
            "uris": [
                "spotify:track:track123",
                "spotify:episode:episode456",
            ],
            "position": 3,
        }

    def test_add_items_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.add_items(
                    "",
                    ["spotify:track:track123"],
                )

    def test_add_items_empty_uris_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="uris cannot be empty"):
                client.playlists.add_items("playlist123", [])


class TestPlaylistServiceRemoveItems:
    def test_remove_items_by_uris(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.spotify.com/v1/playlists/playlist123/tracks",
            json=SNAPSHOT_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            snapshot_id = client.playlists.remove_items(
                "playlist123",
                uris=["spotify:track:track123", "spotify:episode:episode456"],
                snapshot_id="snapshot-123",
            )

        assert snapshot_id == "snapshot-456"
        requests = httpx_mock.get_requests()
        assert json.loads(requests[0].content.decode()) == {
            "tracks": [
                {"uri": "spotify:track:track123"},
                {"uri": "spotify:episode:episode456"},
            ],
            "snapshot_id": "snapshot-123",
        }

    def test_remove_items_by_tracks(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.spotify.com/v1/playlists/playlist123/tracks",
            json=SNAPSHOT_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            snapshot_id = client.playlists.remove_items(
                "playlist123",
                tracks=[{"uri": "spotify:track:track123", "positions": [2]}],
            )

        assert snapshot_id == "snapshot-456"
        requests = httpx_mock.get_requests()
        assert json.loads(requests[0].content.decode()) == {
            "tracks": [
                {"uri": "spotify:track:track123", "positions": [2]},
            ]
        }

    def test_remove_items_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.remove_items(
                    "",
                    uris=["spotify:track:track123"],
                )

    def test_remove_items_requires_exactly_one_payload(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError, match="Provide exactly one of uris or tracks"
            ):
                client.playlists.remove_items("playlist123")

            with pytest.raises(
                ValueError, match="Provide exactly one of uris or tracks"
            ):
                client.playlists.remove_items(
                    "playlist123",
                    uris=["spotify:track:track123"],
                    tracks=[{"uri": "spotify:track:track456"}],
                )

    def test_remove_items_track_missing_uri_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="Each track must include a non-empty uri",
            ):
                client.playlists.remove_items(
                    "playlist123",
                    tracks=[{"positions": [1]}],  # type: ignore[list-item]
                )

    def test_remove_items_track_invalid_positions_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="positions must be a list of integers",
            ):
                client.playlists.remove_items(
                    "playlist123",
                    tracks=[
                        {
                            "uri": "spotify:track:track123",
                            "positions": "bad",  # type: ignore[dict-item]
                        }
                    ],
                )


class TestPlaylistServiceGetCoverImage:
    def test_get_cover_image(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.spotify.com/v1/playlists/playlist123/images",
            json=IMAGE_RESPONSE,
        )

        with SpotifyClient(access_token="test-token") as client:
            images = client.playlists.get_cover_image("playlist123")

        assert len(images) == 1
        assert isinstance(images[0], Image)
        assert images[0].url == "https://i.scdn.co/image/playlist-cover"

    def test_get_cover_image_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.get_cover_image("")


class TestPlaylistServiceUploadCoverImage:
    def test_upload_cover_image(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.spotify.com/v1/playlists/playlist123/images",
            status_code=202,
        )

        image_payload = "/9j/4AAQSkZJRgABAQAAAQABAAD/"

        with SpotifyClient(access_token="test-token") as client:
            client.playlists.upload_cover_image(
                "playlist123",
                image_payload,
            )

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].headers["Content-Type"] == "image/jpeg"
        assert requests[0].content.decode() == image_payload

    def test_upload_cover_image_empty_id_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="id cannot be empty"):
                client.playlists.upload_cover_image(
                    "",
                    "/9j/4AAQSkZJRgABAQAAAQABAAD/",
                )

    def test_upload_cover_image_empty_payload_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="image_base64_jpeg cannot be empty",
            ):
                client.playlists.upload_cover_image("playlist123", "")
