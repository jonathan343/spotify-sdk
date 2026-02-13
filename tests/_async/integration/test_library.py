"""Integration tests for the library service."""

from __future__ import annotations

import os

import anyio
import pytest

from spotify_sdk import AsyncSpotifyClient
from spotify_sdk._async.auth import (
    ENV_CLIENT_ID,
    ENV_CLIENT_SECRET,
    ENV_REDIRECT_URI,
    AsyncAuthorizationCode,
)
from spotify_sdk.auth import async_authorize_local

DEFAULT_TEST_URI = "spotify:track:548pWs8FmBjkr3Qqm2TdPQ"
LIBRARY_SCOPES = ("user-library-read", "user-library-modify")


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


async def _eventually_contains(
    client: AsyncSpotifyClient,
    uris: list[str],
    expected: bool,
    *,
    attempts: int = 8,
    delay_seconds: float = 0.5,
) -> list[bool]:
    for _ in range(attempts):
        result = await client.library.check_contains(uris)
        if result == [expected] * len(uris):
            return result
        await anyio.sleep(delay_seconds)

    return await client.library.check_contains(uris)


class TestLibraryServiceIntegration:
    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_save_check_remove_roundtrip(self):
        _require_credentials()

        uris = [DEFAULT_TEST_URI]

        auth = AsyncAuthorizationCode(scope=list(LIBRARY_SCOPES))
        await async_authorize_local(auth)

        async with AsyncSpotifyClient(auth_provider=auth) as client:
            # Start from a known state for the test URI.
            await client.library.remove_items(uris)
            initial_state = await _eventually_contains(
                client,
                uris,
                expected=False,
            )
            assert initial_state == [False]

            try:
                await client.library.save_items(uris)
                saved_state = await _eventually_contains(
                    client,
                    uris,
                    expected=True,
                )
                assert saved_state == [True]
            finally:
                # Cleanup should run even if assertions fail.
                await client.library.remove_items(uris)

            final_state = await _eventually_contains(
                client,
                uris,
                expected=False,
            )
            assert final_state == [False]
