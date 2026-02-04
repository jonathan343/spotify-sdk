---
icon: lucide/book
---

# Chapters

Chapter operations live under `client.chapters`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Chapter` | Fetch a chapter by Spotify ID |
| `get_several(ids, market=None)` | `list[Chapter]` | Fetch multiple chapters (max 50 IDs) |

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        chapter = client.chapters.get("example_chapter_id")
        chapters = client.chapters.get_several(
            ["example_chapter_id", "another_chapter_id"],
        )
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            chapter = await client.chapters.get("example_chapter_id")
            chapters = await client.chapters.get_several(
                ["example_chapter_id", "another_chapter_id"],
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.chapters.AsyncChapterService
