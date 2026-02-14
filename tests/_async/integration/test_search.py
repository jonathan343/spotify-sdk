"""Integration tests for the search service."""

from __future__ import annotations

import os

import pytest

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk._async.auth import ENV_CLIENT_ID, ENV_CLIENT_SECRET


def _require_credentials() -> None:
    required = [
        ENV_CLIENT_ID,
        ENV_CLIENT_SECRET,
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        pytest.fail(
            "Missing required integration env vars: "
            f"{', '.join(sorted(missing))}",
            pytrace=False,
        )


class TestSearchServiceIntegration:
    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_search_artists_with_client_credentials(self):
        _require_credentials()

        async with AsyncSpotifyClient.from_client_credentials() as client:
            result = await client.search.search(
                q="miles davis",
                types=["artist"],
                market="US",
                limit=5,
                offset=0,
            )

        assert result.artists is not None
        assert result.artists.limit == 5
        assert result.artists.offset == 0
        assert result.artists.total >= len(result.artists.items)
        if result.artists.items:
            assert result.artists.items[0].type_ == "artist"
