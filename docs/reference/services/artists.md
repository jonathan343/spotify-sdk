---
icon: lucide/mic-2
---

# Artists

Artist operations live under `client.artists`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id)` | `Artist` | Fetch an artist by Spotify ID |
| `get_several(ids)` | `list[Artist]` | Fetch multiple artists (max 50 IDs) |
| `get_albums(id, include_groups=None, market=None, limit=None, offset=None)` | `Page[SimplifiedAlbum]` | Fetch albums for an artist |
| `get_top_tracks(id, market=None)` | `list[Track]` | Fetch an artist's top tracks |

!!! tip "Filtering album types"
    `include_groups` accepts the values `album`, `single`, `appears_on`, and
    `compilation`. Pass a list to filter results.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        artist = client.artists.get("3TVXtAsR1Inumwj472S9r4")
        albums = client.artists.get_albums(
            artist.id,
            include_groups=["album", "single"],
            limit=10,
        )
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            artist = await client.artists.get("3TVXtAsR1Inumwj472S9r4")
            albums = await client.artists.get_albums(
                artist.id,
                include_groups=["album", "single"],
                limit=10,
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.artists.AsyncArtistService
