---
icon: lucide/play
---

# Player

Player operations live under `client.player`.

## Methods

| Method | Returns | Description |
| --- | --- | --- |
| `get_playback_state(market=None, additional_types=None)` | `PlaybackState \| None` | Fetch the current playback state |
| `transfer_playback(device_id, play=None)` | `None` | Transfer playback to another device |
| `get_devices()` | `list[PlayerDevice]` | Fetch available playback devices |
| `get_currently_playing(market=None, additional_types=None)` | `CurrentlyPlaying \| None` | Fetch the currently playing item |
| `start_playback(device_id=None, *, context_uri=None, uris=None, offset=None, position_ms=None)` | `None` | Start or resume playback |
| `pause_playback(device_id=None)` | `None` | Pause playback |
| `skip_to_next(device_id=None)` | `None` | Skip to the next item |
| `skip_to_previous(device_id=None)` | `None` | Skip to the previous item |
| `seek(position_ms, device_id=None)` | `None` | Seek within the current item |
| `set_repeat_mode(state, device_id=None)` | `None` | Set repeat mode |
| `set_volume(volume_percent, device_id=None)` | `None` | Set device volume |
| `set_shuffle(state, device_id=None)` | `None` | Enable or disable shuffle |
| `get_recently_played(limit=None, after=None, before=None)` | `RecentlyPlayedPage` | Fetch recently played tracks |
| `get_queue()` | `PlaybackQueue` | Fetch the current playback queue |
| `add_to_queue(uri, device_id=None)` | `None` | Add an item to the playback queue |

!!! tip "Required scopes"
    Spotify requires user-scoped access tokens for player endpoints. Common
    scopes include `user-read-playback-state`, `user-modify-playback-state`,
    and `user-read-recently-played`.

!!! tip "Playback items"
    Playback responses may contain either tracks or episodes. Pass
    `additional_types=["episode"]` or `["track", "episode"]` when you want
    episode playback to be included in the response.

## Examples

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        devices = client.player.get_devices()
        playback = client.player.get_playback_state(
            market="US",
            additional_types=["track", "episode"],
        )
        client.player.start_playback(
            context_uri="spotify:playlist:FAKE_PLAYLIST_ID_123",
            offset=0,
        )
        client.player.set_volume(65)
        client.player.add_to_queue("spotify:track:FAKE_TRACK_ID_456")
        recent = client.player.get_recently_played(limit=5)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            devices = await client.player.get_devices()
            playback = await client.player.get_currently_playing(
                market="US",
                additional_types=["episode"],
            )
            await client.player.transfer_playback(
                "FAKE_DEVICE_ID_123",
                play=True,
            )
            await client.player.start_playback(
                device_id="FAKE_DEVICE_ID_123",
                uris=[
                    "spotify:track:FAKE_TRACK_ID_456",
                    "spotify:episode:FAKE_EPISODE_ID_789",
                ],
                offset=1,
                position_ms=30_000,
            )
            queue = await client.player.get_queue()

    asyncio.run(main())
    ```

## API details

The sync client mirrors these methods, minus the `await` keywords.

::: spotify_sdk._async.services.player.AsyncPlayerService
