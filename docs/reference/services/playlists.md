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
| `create(user_id, name, public=None, collaborative=None, description=None)` | `SimplifiedPlaylist` | Create a playlist for a user |
| `change_details(id, name=None, public=None, collaborative=None, description=None)` | `None` | Update playlist metadata |
| `reorder_or_replace_items(id, uris=None, range_start=None, insert_before=None, range_length=None, snapshot_id=None)` | `str` | Reorder existing items or replace all items |
| `add_items(id, uris, position=None)` | `str` | Add items to a playlist |
| `remove_items(id, *, uris=None, tracks=None, snapshot_id=None)` | `str` | Remove items from a playlist |
| `get_cover_image(id)` | `list[Image]` | Fetch playlist cover images |
| `upload_cover_image(id, image_base64_jpeg)` | `None` | Upload a custom playlist cover image |

!!! tip "Field filtering"
    The `fields` parameter supports Spotify's field filtering syntax, letting
    you request a subset of fields for large playlist payloads.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        playlist = client.playlists.create(
            user_id="spotify_user_123",
            name="Road Trip Mix",
            public=False,
            description="Songs for a long drive",
        )
        client.playlists.add_items(
            playlist.id,
            ["spotify:track:FAKE_TRACK_ID_123"],
        )
        client.playlists.change_details(
            playlist.id,
            name="Road Trip Mix 2026",
        )
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            playlist = await client.playlists.create(
                user_id="spotify_user_123",
                name="Road Trip Mix",
                public=False,
            )
            await client.playlists.add_items(
                playlist.id,
                ["spotify:track:FAKE_TRACK_ID_123"],
            )
            snapshot_id = await client.playlists.reorder_or_replace_items(
                playlist.id,
                range_start=0,
                insert_before=1,
            )
            await client.playlists.remove_items(
                playlist.id,
                uris=["spotify:track:FAKE_TRACK_ID_123"],
                snapshot_id=snapshot_id,
            )
            await client.playlists.upload_cover_image(
                playlist.id,
                "<base64-jpeg-data>",
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.playlists.AsyncPlaylistService
