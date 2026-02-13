"""Tests for the library service."""

import pytest
from pytest_httpx import HTTPXMock

from spotify_sdk import SpotifyClient

TRACK_URI = "spotify:track:7a3LWj5xSFhFRYmztS8wgK"
ALBUM_URI = "spotify:album:4aawyAB9vmqN3uQ7FjRGTy"


class TestLibraryServiceSaveItems:
    def test_save_items(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="PUT",
            url=(
                "https://api.spotify.com/v1/me/library"
                "?uris=spotify%3Atrack%3A7a3LWj5xSFhFRYmztS8wgK%2C"
                "spotify%3Aalbum%3A4aawyAB9vmqN3uQ7FjRGTy"
            ),
            status_code=200,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.library.save_items([TRACK_URI, ALBUM_URI])

    def test_save_items_empty_uris_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="uris cannot be empty"):
                client.library.save_items([])

    def test_save_items_too_many_uris_raises_error(self):
        uris = [f"spotify:track:{i}" for i in range(41)]
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="maximum of 40 URIs",
            ):
                client.library.save_items(uris)

    def test_save_items_empty_uri_value_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(
                ValueError,
                match="uris cannot contain empty values",
            ):
                client.library.save_items([TRACK_URI, ""])


class TestLibraryServiceRemoveItems:
    def test_remove_items(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=(
                "https://api.spotify.com/v1/me/library"
                "?uris=spotify%3Atrack%3A7a3LWj5xSFhFRYmztS8wgK"
            ),
            status_code=200,
        )

        with SpotifyClient(access_token="test-token") as client:
            client.library.remove_items([TRACK_URI])

    def test_remove_items_empty_uris_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="uris cannot be empty"):
                client.library.remove_items([])


class TestLibraryServiceCheckContains:
    def test_check_contains(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=(
                "https://api.spotify.com/v1/me/library/contains"
                "?uris=spotify%3Atrack%3A7a3LWj5xSFhFRYmztS8wgK%2C"
                "spotify%3Aalbum%3A4aawyAB9vmqN3uQ7FjRGTy"
            ),
            json=[True, False],
        )

        with SpotifyClient(access_token="test-token") as client:
            result = client.library.check_contains([
                TRACK_URI,
                ALBUM_URI,
            ])

        assert result == [True, False]

    def test_check_contains_empty_uris_raises_error(self):
        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="uris cannot be empty"):
                client.library.check_contains([])

    def test_check_contains_invalid_shape_raises_error(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            method="GET",
            url=(
                "https://api.spotify.com/v1/me/library/contains"
                "?uris=spotify%3Atrack%3A7a3LWj5xSFhFRYmztS8wgK"
            ),
            json={"unexpected": True},
        )

        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Expected list response"):
                client.library.check_contains([TRACK_URI])

    def test_check_contains_invalid_item_type_raises_error(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            method="GET",
            url=(
                "https://api.spotify.com/v1/me/library/contains"
                "?uris=spotify%3Atrack%3A7a3LWj5xSFhFRYmztS8wgK"
            ),
            json=[True, "nope"],
        )

        with SpotifyClient(access_token="test-token") as client:
            with pytest.raises(ValueError, match="Expected list\\[bool\\]"):
                client.library.check_contains([TRACK_URI])
