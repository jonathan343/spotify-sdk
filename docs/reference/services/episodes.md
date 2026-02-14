---
icon: lucide/radio
---

# Episodes

Episode operations live under `client.episodes`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get(id, market=None)` | `Episode` | Fetch a single episode by Spotify ID |
| `get_saved(limit=20, offset=0, market=None)` | `Page[SavedEpisode]` | Fetch current user's saved episodes |

!!! tip "Required scopes"
    Spotify requires a user-scoped access token for `get_saved`.
    Ensure your auth flow requests `user-library-read`.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        episode = client.episodes.get("episode_id_123")
        saved_episodes = client.episodes.get_saved(limit=10)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            episode = await client.episodes.get("episode_id_123")
            saved_episodes = await client.episodes.get_saved(limit=10)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.episodes.AsyncEpisodeService
