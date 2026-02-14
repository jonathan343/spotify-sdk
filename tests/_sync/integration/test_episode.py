"""Integration tests for the episode service."""

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

EPISODE_SCOPES = ("user-library-read",)


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


class TestEpisodeServiceIntegration:
    @pytest.mark.integration
    def test_get_and_get_saved(self):
        _require_credentials()

        auth = AuthorizationCode(scope=list(EPISODE_SCOPES))
        authorize_local(auth)

        with SpotifyClient(auth_provider=auth) as client:
            saved_episodes = client.episodes.get_saved(limit=5, offset=0)
            assert saved_episodes.limit == 5
            assert saved_episodes.offset == 0

            if not saved_episodes.items:
                pytest.skip(
                    "No saved episodes available for this account. "
                    "Save at least one episode to run this test."
                )

            episode_id = saved_episodes.items[0].episode.id

            episode = client.episodes.get(episode_id)
            assert episode.id == episode_id
            assert episode.type_ == "episode"
