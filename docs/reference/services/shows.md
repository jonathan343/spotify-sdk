---
icon: lucide/podcast
---

# Shows

Show operations live under `client.shows`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Show` | Fetch a single show by Spotify ID |
| `get_episodes(id, market=None, limit=20, offset=0)` | `Page[SimplifiedEpisode]` | Fetch episodes for a show |
| `get_saved(limit=20, offset=0)` | `Page[SavedShow]` | Fetch current user's saved shows |

!!! tip "Required scopes"
    Spotify requires a user-scoped access token for `get_saved`.
    Ensure your auth flow requests `user-library-read`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        show = client.shows.get("show_id_123")
        episodes = client.shows.get_episodes(show.id, limit=10)
        saved_shows = client.shows.get_saved(limit=10)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            show = await client.shows.get("show_id_123")
            episodes = await client.shows.get_episodes(show.id, limit=10)
            saved_shows = await client.shows.get_saved(limit=10)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.shows.AsyncShowService
