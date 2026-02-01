---
icon: lucide/music-2
---

# Tracks

Track operations live under `client.tracks`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Track` | Fetch a track by Spotify ID |
| `get_several(ids, market=None)` | `list[Track]` | Fetch multiple tracks (max 20 IDs) |

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        track = client.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
        tracks = client.tracks.get_several(
            ["3n3Ppam7vgaVa1iaRUc9Lp", "7ouMYWpwJ422jRcDASZB7P"],
        )
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            track = await client.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
            tracks = await client.tracks.get_several(
                ["3n3Ppam7vgaVa1iaRUc9Lp", "7ouMYWpwJ422jRcDASZB7P"],
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.tracks.AsyncTrackService
