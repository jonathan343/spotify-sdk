"""Integration tests for the show service."""

from __future__ import annotations

import os

import pytest

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk._async.auth import (
    ENV_CLIENT_ID,
    ENV_CLIENT_SECRET,
    ENV_REDIRECT_URI,
    AsyncAuthorizationCode,
)
from spotify_sdk.auth import async_authorize_local

# Public show ID from Spotify's Web API docs.
DEFAULT_TEST_SHOW_ID = "6PwE1CIZsgfrhX6Bw96PUN"
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
    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_get_get_episodes_and_get_saved(self):
        _require_credentials()

        auth = AsyncAuthorizationCode(scope=list(SHOW_SCOPES))
        await async_authorize_local(auth)

        async with AsyncSpotifyClient(auth_provider=auth) as client:
            show = await client.shows.get(DEFAULT_TEST_SHOW_ID, market="US")
            assert show.id == DEFAULT_TEST_SHOW_ID
            assert show.type_ == "show"

            episodes = await client.shows.get_episodes(
                DEFAULT_TEST_SHOW_ID,
                market="US",
                limit=5,
                offset=0,
            )
            assert episodes.limit == 5
            assert episodes.offset == 0
            assert all(item.type_ == "episode" for item in episodes.items)

            saved_shows = await client.shows.get_saved(limit=5, offset=0)
            assert saved_shows.limit == 5
            assert saved_shows.offset == 0
