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
| `follow_playlist(id, public=None)` | `None` | Follow a playlist as the current user |
| `unfollow_playlist(id)` | `None` | Unfollow a playlist as the current user |
| `follow_artists_or_users(type_, ids)` | `None` | Follow artists or users |
| `unfollow_artists_or_users(type_, ids)` | `None` | Unfollow artists or users |
| `check_follows_artists_or_users(type_, ids)` | `list[bool]` | Check if current user follows artists or users |
| `check_if_follows_playlist(id, user_ids)` | `list[bool]` | Check if users follow a playlist |

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for these endpoints. Ensure your
    auth flow requests scopes such as `user-read-private` and
    `user-top-read`, `user-follow-read`, and `user-follow-modify`, plus
    playlist scopes when following/checking playlists.

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
        artist_follow_flags = client.users.check_follows_artists_or_users(
            "artist",
            ["example_artist_id"],
        )
        client.users.follow_playlist("example_playlist_id", public=False)
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
            artist_follow_flags = await client.users.check_follows_artists_or_users(
                "artist",
                ["example_artist_id"],
            )
            await client.users.follow_playlist(
                "example_playlist_id",
                public=False,
            )

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.users.AsyncUserService
