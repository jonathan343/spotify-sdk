---
icon: lucide/music-2
---

# Tracks

Track operations live under `client.tracks`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Track` | Fetch a track by Spotify ID |
| `get_saved(limit=20, offset=0, market=None)` | `Page[SavedTrack]` | Fetch current user's saved tracks |

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for saved track access.
    Ensure your auth flow requests `user-library-read` when using `get_saved`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        track = client.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
        saved_tracks = client.tracks.get_saved(limit=10)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            track = await client.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
            saved_tracks = await client.tracks.get_saved(limit=10)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.tracks.AsyncTrackService
