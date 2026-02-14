"""Integration tests for the show service."""

from __future__ import annotations

import os

import pytest

from spotify_sdk import SpotifyClient
from spotify_sdk._sync.auth import (
    ENV_CLIENT_ID,
    ENV_CLIENT_SECRET,
    ENV_REDIRECT_URI,
    AuthorizationCode,
)
from spotify_sdk.auth import authorize_local

SHOW_SCOPES = ("user-library-read",)


def _require_credentials() -> None:
    required = [
        ENV_CLIENT_ID,
        ENV_CLIENT_SECRET,
        ENV_REDIRECT_URI,
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        pytest.fail(
            "Missing required integration env vars: "
            f"{', '.join(sorted(missing))}",
            pytrace=False,
        )


class TestShowServiceIntegration:
    @pytest.mark.integration
    def test_get_get_episodes_and_get_saved(self):
        _require_credentials()

        auth = AuthorizationCode(scope=list(SHOW_SCOPES))
        authorize_local(auth)

        with SpotifyClient(auth_provider=auth) as client:
            saved_shows = client.shows.get_saved(limit=5, offset=0)
            assert saved_shows.limit == 5
            assert saved_shows.offset == 0

            if not saved_shows.items:
                pytest.skip(
                    "No saved shows available for this account. "
                    "Save at least one show to run this test."
                )

            show_id = saved_shows.items[0].show.id

            show = client.shows.get(show_id)
            assert show.id == show_id
            assert show.type_ == "show"

            episodes = client.shows.get_episodes(
                show_id,
                limit=5,
                offset=0,
            )
            assert episodes.limit == 5
            assert episodes.offset == 0
            assert all(item.type_ == "episode" for item in episodes.items)
