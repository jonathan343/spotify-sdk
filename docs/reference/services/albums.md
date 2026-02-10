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
| `get_saved(limit=20, offset=0, market=None)` | `Page[SavedAlbum]` | Fetch current user's saved albums |
| `check_saved(ids)` | `list[bool]` | Check if albums are saved in current user's library |

!!! tip "Market parameter"
    Pass an ISO 3166-1 alpha-2 country code to `market` when you need
    relinking for regional availability.

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for library endpoints.
    Ensure your auth flow requests `user-library-read` when using
    `get_saved` or `check_saved`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        album = client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
        tracks = client.albums.get_tracks(album.id, limit=10)
        saved_albums = client.albums.get_saved(limit=10)
        saved_flags = client.albums.check_saved(["example_album_id"])
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            album = await client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
            tracks = await client.albums.get_tracks(album.id, limit=10)
            saved_albums = await client.albums.get_saved(limit=10)
            saved_flags = await client.albums.check_saved(
                ["example_album_id"]
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.albums.AsyncAlbumService
