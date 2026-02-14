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
| `access_token` | `str` | optional | Spotify access token (mutually exclusive with other auth inputs) |
| `client_id` | `str` | optional | Spotify client ID (client credentials flow) |
| `client_secret` | `str` | optional | Spotify client secret (client credentials flow) |
| `auth_provider` | `AuthProvider` | optional | Custom auth provider (mutually exclusive with other auth inputs) |
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

### Client Credentials

Use client credentials to let the SDK obtain and refresh tokens automatically.

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    client = SpotifyClient.from_client_credentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    ```

=== "Async"

    ```python
    from spotify_sdk import AsyncSpotifyClient

    client = AsyncSpotifyClient.from_client_credentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    ```

### Custom Auth Provider

Pass a custom auth provider instance for advanced or future flows.

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient
    from spotify_sdk.auth import ClientCredentials

    auth = ClientCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    client = SpotifyClient(auth_provider=auth)
    ```

=== "Async"

    ```python
    from spotify_sdk import AsyncSpotifyClient
    from spotify_sdk.auth import AsyncClientCredentials

    auth = AsyncClientCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    client = AsyncSpotifyClient(auth_provider=auth)
    ```

### Environment Variables

If `client_id` or `client_secret` are omitted, the SDK reads:

- `SPOTIFY_SDK_CLIENT_ID`
- `SPOTIFY_SDK_CLIENT_SECRET`

Explicit arguments override environment variables.

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
| `client.audiobooks` | Audiobook operations |
| `client.chapters` | Chapter operations |
| `client.library` | Save, remove, and check library items |
| `client.playlists` | Playlist operations |
| `client.shows` | Show operations |
| `client.tracks` | Track operations |
| `client.users` | Current user and profile operations |

See the full service reference for method-level details.
