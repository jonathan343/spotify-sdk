---
icon: lucide/book
---

# Audiobooks

Audiobook operations live under `client.audiobooks`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Audiobook` | Fetch a single audiobook by Spotify ID |
| `get_several(ids, market=None)` | `list[Audiobook]` | Fetch multiple audiobooks (max 50 IDs) |
| `get_chapters(id, market=None, limit=20, offset=0)` | `Page[SimplifiedChapter]` | Fetch chapters for an audiobook |

!!! tip "Market parameter"
    Pass an ISO 3166-1 alpha-2 country code to `market` to ensure availability.

!!! note "Limited availability"
    Audiobooks are currently available only in select markets.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        audiobook = client.audiobooks.get("7iHfbu1YPACw6oZPAFJtqe")
        chapters = client.audiobooks.get_chapters(audiobook.id, limit=10)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            audiobook = await client.audiobooks.get("7iHfbu1YPACw6oZPAFJtqe")
            chapters = await client.audiobooks.get_chapters(audiobook.id, limit=10)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.audiobooks.AsyncAudiobookService
