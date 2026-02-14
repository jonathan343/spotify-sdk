---
icon: lucide/layers
---

# Services

Each service wraps a portion of the Spotify Web API. Services are exposed as
attributes on the client instance.

!!! note "Auto-generated API details"
    Each service page includes an auto-generated API section rendered from the
    async implementation, which is the canonical source for the SDK.

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        album = client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            album = await client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")

    asyncio.run(main())
    ```

## Service list

| Service | Description |
| --- | --- |
| [Albums](albums.md) | Album details, tracks, and new releases |
| [Audiobooks](audiobooks.md) | Audiobook details and chapter lookups |
| [Chapters](chapters.md) | Chapter details and bulk lookups |
| [Artists](artists.md) | Artist profiles, albums, and top tracks |
| [Library](library.md) | Save, remove, and check items in the user's library |
| [Playlists](playlists.md) | Playlist details, items, and images |
| [Shows](shows.md) | Show details, episode lists, and saved shows |
| [Tracks](tracks.md) | Track details and bulk lookups |
| [Users](users.md) | Current-user profile, top items, and playlist follows |
