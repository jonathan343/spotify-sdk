---
icon: lucide/search
---

# Search

Search operations live under `client.search`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `search(q, types, market=None, limit=5, offset=0, include_external=None)` | `SearchResult` | Search Spotify catalog resources by query |

!!! tip "Type values"
    Supported values for `types` are: `album`, `artist`, `playlist`, `track`,
    `show`, `episode`, and `audiobook`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        result = client.search.search(
            q="kind of blue",
            types=["album", "artist"],
            market="US",
            limit=10,
        )
        albums = result.albums.items if result.albums else []
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            result = await client.search.search(
                q="kind of blue",
                types=["album", "artist"],
                market="US",
                limit=10,
            )
            artists = result.artists.items if result.artists else []

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.search.AsyncSearchService
