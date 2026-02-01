---
icon: lucide/list-music
---

# Playlists

Playlist operations live under `client.playlists`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None, fields=None)` | `Playlist` | Fetch a playlist by ID |
| `get_items(id, market=None, fields=None, limit=None, offset=None)` | `Page[PlaylistTrack]` | Fetch playlist items |
| `get_for_current_user(limit=None, offset=None)` | `Page[SimplifiedPlaylist]` | Fetch playlists for the current user |
| `get_for_user(id, limit=None, offset=None)` | `Page[SimplifiedPlaylist]` | Fetch playlists for a specific user |
| `get_cover_image(id)` | `list[Image]` | Fetch playlist cover images |

!!! tip "Field filtering"
    The `fields` parameter supports Spotify's field filtering syntax, letting
    you request a subset of fields for large playlist payloads.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        playlist = client.playlists.get("37i9dQZF1DXcBWIGoYBM5M")
        items = client.playlists.get_items(playlist.id, limit=50)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            playlist = await client.playlists.get("37i9dQZF1DXcBWIGoYBM5M")
            items = await client.playlists.get_items(playlist.id, limit=50)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.playlists.AsyncPlaylistService
