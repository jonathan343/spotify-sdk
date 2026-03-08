---
icon: lucide/user-round
---

# Users

User operations live under `client.users`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get_current_profile()` | `CurrentUser` | Fetch the current user's profile |
| `get_top_artists(time_range=None, limit=None, offset=None)` | `Page[Artist]` | Fetch the current user's top artists |
| `get_top_tracks(time_range=None, limit=None, offset=None)` | `Page[Track]` | Fetch the current user's top tracks |
| `get_followed_artists(after=None, limit=None)` | `CursorPage[Artist]` | Fetch artists followed by the current user |

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for these endpoints. Request the
    scopes that match the methods you call: `user-read-private` for
    `get_current_profile()`, `user-top-read` for top artists and tracks, and
    `user-follow-read` for `get_followed_artists()`. For follow management and
    saved-item checks, use `client.library` instead.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        me = client.users.get_current_profile()
        top_tracks = client.users.get_top_tracks(
            time_range="short_term",
            limit=5,
        )
        followed = client.users.get_followed_artists(limit=5)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            me = await client.users.get_current_profile()
            top_tracks = await client.users.get_top_tracks(
                time_range="short_term",
                limit=5,
            )
            followed = await client.users.get_followed_artists(limit=5)

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.users.AsyncUserService
