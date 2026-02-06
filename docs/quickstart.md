---
icon: lucide/rocket
---

# Quickstart

This guide covers the basics of using the Spotify SDK.

## Authentication

The SDK supports access tokens, client credentials, and authorization code
auth. You can supply an access token directly or let the SDK obtain and
refresh tokens for you.

!!! tip "Getting credentials"
    Visit the Spotify Developer Dashboard to create an app and obtain a client
    ID and client secret. Use Spotify's authorization flows to get user tokens
    when accessing `/me/*` endpoints.

## Basic Usage

### Synchronous Client

```python
from spotify_sdk import SpotifyClient

with SpotifyClient(access_token="your-access-token") as client:
    # Get an album
    album = client.albums.get("4Uv86qWpGTxf7fU7lG5X6F")
    print(f"{album.name} by {album.artists[0].name}") # (1)!

    # Get album tracks
    tracks = client.albums.get_tracks(album.id)
    for track in tracks.items:
        print(f"{track.track_number}. {track.name}") # (2)!
```

1. Output: `The College Dropout by Kanye West`

2. Output:
    ```
    1. Intro
    2. We Don't Care
    3. Graduation Day
    4. All Falls Down
    5. I'll Fly Away
    6. Spaceship
    7. Jesus Walks
    8. Never Let Me Down
    9. Get Em High
    10. Workout Plan
    11. The New Workout Plan
    12. Slow Jamz
    13. Breathe In Breathe Out
    14. School Spirit Skit 1
    15. School Spirit
    16. School Spirit Skit 2
    17. Lil Jimmy Skit
    18. Two Words
    19. Through The Wire
    20. Family Business
    ```

### Async Client

```python
import asyncio
from spotify_sdk import AsyncSpotifyClient

async def main():
    async with AsyncSpotifyClient(access_token="your-access-token") as client:
        album = await client.albums.get("4Uv86qWpGTxf7fU7lG5X6F")
        print(f"{album.name} by {album.artists[0].name}") # (1)!

asyncio.run(main())
```

1. Output: `The College Dropout by Kanye West`

## Available Services

| Service | Description |
|---------|-------------|
| `client.albums` | Get albums, album tracks, and multiple albums |
| `client.artists` | Get artists, artist albums, and top tracks |
| `client.playlists` | Get playlists, playlist items, and cover images |
| `client.tracks` | Get tracks and multiple tracks |

## Configuration

Customize client behavior:

```python
client = SpotifyClient(
    access_token="your-access-token",
    timeout=30.0,      # Request timeout in seconds (default: 30.0)
    max_retries=3,     # Maximum retry attempts (default: 3)
)
```

### Client Credentials

Create clients using client credentials (server-to-server).

```python
from spotify_sdk import SpotifyClient

client = SpotifyClient.from_client_credentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

### Authorization Code

Use an authorization code provider for user-scoped endpoints.

```python
from spotify_sdk.auth import AuthorizationCode

auth = AuthorizationCode(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://127.0.0.1:8080/callback",
    scope=["user-read-private"],
)
```

For local scripts, use the helper to avoid manual callback URL copy/paste:

```python
from spotify_sdk.auth import AuthorizationCode, authorize_local

auth = AuthorizationCode(scope="user-read-private")
token_info = authorize_local(auth)
print(token_info.refresh_token)
```

If you're already in async code, use the async helper:

```python
from spotify_sdk.auth import AsyncAuthorizationCode, async_authorize_local

auth = AsyncAuthorizationCode(scope="user-read-private")
token_info = await async_authorize_local(auth)
print(token_info.refresh_token)
```

Add a file cache to persist refresh tokens:

```python
from spotify_sdk.auth import AuthorizationCode, FileTokenCache

auth = AuthorizationCode(
    scope="user-read-private",
    token_cache=FileTokenCache(".cache/spotify-sdk/token.json"),
)
```

### Environment Variables

If you omit `client_id`, `client_secret`, or `redirect_uri`, the SDK reads:

- `SPOTIFY_SDK_CLIENT_ID`
- `SPOTIFY_SDK_CLIENT_SECRET`
- `SPOTIFY_SDK_REDIRECT_URI`

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
