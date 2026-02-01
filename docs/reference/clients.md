---
icon: lucide/terminal
---

# Clients

The SDK exposes two entry points that share the same configuration:
`SpotifyClient` for sync workflows and `AsyncSpotifyClient` for async
workflows.

## Construction

Both clients accept the same constructor arguments.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `access_token` | `str` | required | Spotify access token |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retries for transient errors |

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    client = SpotifyClient(
        access_token="your-access-token",
        timeout=30.0,
        max_retries=3,
    )
    ```

=== "Async"

    ```python
    from spotify_sdk import AsyncSpotifyClient

    client = AsyncSpotifyClient(
        access_token="your-access-token",
        timeout=30.0,
        max_retries=3,
    )
    ```

## Lifecycle

Use context managers to ensure connections are closed. You can also call
`close()`/`await close()` directly.

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        album = client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
        print(album.name)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            album = await client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
            print(album.name)

    asyncio.run(main())
    ```

## Available services

The main client exposes service objects as attributes:

| Attribute | Description |
| --- | --- |
| `client.albums` | Album operations |
| `client.artists` | Artist operations |
| `client.playlists` | Playlist operations |
| `client.tracks` | Track operations |

See the full service reference for method-level details.
