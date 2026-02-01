---
icon: lucide/disc
---

# Albums

Album operations live under `client.albums`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Album` | Fetch a single album by Spotify ID |
| `get_several(ids, market=None)` | `list[Album]` | Fetch multiple albums (max 20 IDs) |
| `get_tracks(id, market=None, limit=20, offset=0)` | `Page[SimplifiedTrack]` | Fetch tracks for an album |
| `get_new_releases(limit=20, offset=0)` | `Page[SimplifiedAlbum]` | Fetch new album releases |

!!! tip "Market parameter"
    Pass an ISO 3166-1 alpha-2 country code to `market` when you need
    relinking for regional availability.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        album = client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
        tracks = client.albums.get_tracks(album.id, limit=10)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            album = await client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
            tracks = await client.albums.get_tracks(album.id, limit=10)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.albums.AsyncAlbumService
