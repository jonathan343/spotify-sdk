---
icon: lucide/bookmark
---

# Library

Library operations live under `client.library`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `save_items(uris)` | `None` | Save items to the current user's library |
| `remove_items(uris)` | `None` | Remove items from the current user's library |
| `check_contains(uris)` | `list[bool]` | Check if items are saved in the current user's library |

!!! tip "URIs and mixed types"
    Pass Spotify URIs (not raw IDs), for example `spotify:track:...`.
    A single call can include mixed URI types. Maximum: 40 URIs.

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for these endpoints.
    Request both `user-library-read` and `user-library-modify`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        uris = [
            "spotify:track:7a3LWj5xSFhFRYmztS8wgK",
            "spotify:album:4aawyAB9vmqN3uQ7FjRGTy",
        ]
        client.library.save_items(uris)
        saved_flags = client.library.check_contains(
            uris,
        )
        client.library.remove_items(uris)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            uris = [
                "spotify:track:7a3LWj5xSFhFRYmztS8wgK",
                "spotify:album:4aawyAB9vmqN3uQ7FjRGTy",
            ]
            await client.library.save_items(uris)
            saved_flags = await client.library.check_contains(
                uris,
            )
            await client.library.remove_items(uris)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.library.AsyncLibraryService
