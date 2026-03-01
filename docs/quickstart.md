---
icon: lucide/rocket
---

# Quickstart

## Basic Usage

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        # Get an album
        album = client.albums.get("<your-album-id>")
        print(f"{album.name} by {album.artists[0].name}")

        # Get album tracks
        tracks = client.albums.get_tracks(album.id)
        for track in tracks.items:
            print(f"{track.track_number}. {track.name}")
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            # Get an album
            album = await client.albums.get("<your-album-id>")
            print(f"{album.name} by {album.artists[0].name}")

            # Get album tracks
            tracks = await client.albums.get_tracks(album.id)
            for track in tracks.items:
                print(f"{track.track_number}. {track.name}")

    asyncio.run(main())
    ```

## Available Services

| Service | Description |
|---------|-------------|
| `client.albums` | Get albums, album tracks, and multiple albums |
| `client.artists` | Get artists, artist albums, and top tracks |
| `client.audiobooks` | Get audiobooks, chapters, and multiple audiobooks |
| `client.chapters` | Get chapters and multiple chapters |
| `client.episodes` | Get episodes and saved episodes |
| `client.library` | Save, remove, and check items in a user's library |
| `client.playlists` | Get playlists, playlist items, and cover images |
| `client.search` | Search the Spotify catalog for albums, artists, tracks, and more |
| `client.shows` | Get shows, show episodes, and saved shows |
| `client.tracks` | Get tracks and multiple tracks |
| `client.users` | Get current profile, top artists/tracks, and follow playlists |

[:octicons-arrow-right-24: Full service reference](reference/services/index.md)

## Authentication

The SDK supports access tokens, client credentials, and authorization code
auth. You can supply an access token directly or let the SDK obtain and
refresh tokens for you.

!!! tip "Getting credentials"
    Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
    to create an app and obtain a client ID and client secret. Use Spotify's
    authorization flows to get user tokens when accessing `/me/*` endpoints.

### Client Credentials

Use client credentials for server-to-server access (no user context).

```python
from spotify_sdk import SpotifyClient

client = SpotifyClient.from_client_credentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

### Authorization Code

Use an authorization code provider for user-scoped endpoints. For local
scripts, `auth.authorize_local()` opens the browser and captures the callback
automatically:

```python
from spotify_sdk import SpotifyClient
from spotify_sdk.auth import AuthorizationCode, FileTokenCache

auth = AuthorizationCode(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://127.0.0.1:8080/callback",
    scope=["user-read-private"],
    token_cache=FileTokenCache(".cache/spotify-sdk/token.json"),
)

auth.authorize_local()

with SpotifyClient(auth_provider=auth) as client:
    ...
```

`auth.authorize_local(...)` requires a loopback redirect URI
(`http://127.0.0.1:<port>/...` or `http://localhost:<port>/...`).

See the [auth reference](reference/auth.md#authorization-code) for the full
manual flow, async helpers, and additional options.

### Environment Variables

If you omit `client_id`, `client_secret`, or `redirect_uri` from any auth
provider, the SDK reads:

- `SPOTIFY_SDK_CLIENT_ID`
- `SPOTIFY_SDK_CLIENT_SECRET`
- `SPOTIFY_SDK_REDIRECT_URI` (authorization code only)

## Configuration

Customize client behavior:

```python
client = SpotifyClient(
    access_token="your-access-token",
    timeout=30.0,      # Request timeout in seconds (default: 30.0)
    max_retries=3,     # Maximum retry attempts (default: 3)
)
```

### Retry Behavior

The SDK automatically retries requests on:

- Connection errors and timeouts
- Rate limit responses (429) - respects `Retry-After` header
- Server errors (5xx)

Retries use exponential backoff with jitter to avoid thundering herd problems.

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from spotify_sdk import (
    SpotifyClient,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

try:
    album = client.albums.get("invalid_id")
except NotFoundError as e:
    print(f"Album not found: {e.message}")
except AuthenticationError as e:
    print(f"Invalid token: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

### Exception Reference

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `SpotifyError` | - | Base exception for all SDK errors |
| `AuthenticationError` | 401 | Invalid or expired access token |
| `BadRequestError` | 400 | Invalid request parameters |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ServerError` | 5xx | Spotify server error |
