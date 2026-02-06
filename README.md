# Spotify SDK for Python

[![PyPI version](https://img.shields.io/pypi/v/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Actions status](https://github.com/jonathan343/spotify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/jonathan343/spotify-sdk/actions)
[![Documentation](https://img.shields.io/badge/docs-spotify--sdk.dev-blue.svg)](https://spotify-sdk.dev/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Python SDK for the [Spotify Web API](https://developer.spotify.com/documentation/web-api).

Full documentation is available at **[spotify-sdk.dev](https://spotify-sdk.dev/)**.

> [!NOTE] 
> This is an independent, community-developed library and is not affiliated with or endorsed by Spotify.

## Features

- **Type-safe**: Full type hints with Pydantic models for all API responses
- **Sync and async**: Dedicated `SpotifyClient` and `AsyncSpotifyClient` classes
- **Automatic retries**: Exponential backoff with jitter for rate limits and transient errors
- **Context managers**: Clean resource management with `with` and `async with` support

## Installation

```bash
pip install spotify-sdk
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add spotify-sdk
```

### Requirements

- Python 3.10+

Python version support follows the [official Python release cycle](https://devguide.python.org/versions/). We support all versions that have not reached end-of-life.

## Authentication

The SDK supports:

- [Access token](https://developer.spotify.com/documentation/web-api/concepts/access-token) authentication
- Client credentials flow
- Authorization code flow with refresh tokens

```python
# Access token
client = SpotifyClient(access_token="your-access-token")

# Client credentials
client = SpotifyClient.from_client_credentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

```python
# Authorization code (user-scoped endpoints)
from spotify_sdk.auth import AuthorizationCode, FileTokenCache, authorize_local

auth = AuthorizationCode(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://127.0.0.1:8080/callback",
    scope=["user-read-private"],
    token_cache=FileTokenCache(".cache/spotify-sdk/token.json"),
)

# Local helper: opens browser and captures the callback automatically
authorize_local(auth)

client = SpotifyClient(auth_provider=auth)
```

## Quick Start

```python
from spotify_sdk import SpotifyClient

client = SpotifyClient(access_token="your-access-token")

# Get an album
album = client.albums.get("5K79FLRUCSysQnVESLcTdb")
print(f"{album.name} by {album.artists[0].name}")
# Output: "DeBÍ TiRAR MáS FOToS by Bad Bunny"

# Get album tracks
tracks = client.albums.get_tracks(album.id)
for track in tracks.items:
    print(f"{track.track_number}. {track.name}")

client.close()
```

### Using Context Managers

```python
from spotify_sdk import SpotifyClient

with SpotifyClient(access_token="your-access-token") as client:
    album = client.albums.get("4aawyAB9vmqN3uQ7FjRGTy")
    print(album.name)
```

### Async Support

```python
import asyncio
from spotify_sdk import AsyncSpotifyClient

async def main():
    async with AsyncSpotifyClient(access_token="your-access-token") as client:
        album = await client.albums.get("4Uv86qWpGTxf7fU7lG5X6F")
        print(f"{album.name} by {album.artists[0].name}")
        # "The College Dropout by Kanye West"

asyncio.run(main())
```

## Services

### Albums

```python
# Get a single album
album = client.albums.get("<id>")
album = client.albums.get("<id>", market="US")

# Get multiple albums (up to 20)
albums = client.albums.get_several(["<id1>", "<id2>"])

# Get album tracks with pagination
tracks = client.albums.get_tracks("<id>", limit=10, offset=0)
```

### Audiobooks

```python
# Get a single audiobook
audiobook = client.audiobooks.get("<id>")
audiobook = client.audiobooks.get("<id>", market="US")

# Get multiple audiobooks (up to 50)
audiobooks = client.audiobooks.get_several(["<id1>", "<id2>"])

# Get audiobook chapters with pagination
chapters = client.audiobooks.get_chapters("<id>", limit=10, offset=0)
```

## Error Handling

The SDK raises specific exceptions for different error types:

```python
from spotify_sdk import (
    SpotifyClient,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

try:
    album = client.albums.get("invalid_id")
except NotFoundError as e:
    print(f"Album not found: {e.message}")
except AuthenticationError as e:
    print(f"Invalid token: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ServerError as e:
    print(f"Spotify server error: {e.message}")
```

### Exception Hierarchy

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `SpotifyError` | - | Base exception for all SDK errors |
| `AuthenticationError` | 401 | Invalid or expired access token |
| `BadRequestError` | 400 | Invalid request parameters |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ServerError` | 5xx | Spotify server error |

## Configuration

### Client Options

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

Retries use exponential backoff with jitter:

- Initial delay: 0.5 seconds
- Maximum delay: 8.0 seconds
- Multiplier: 2x per retry

## Models

All API responses are returned as Pydantic models with full type hints:

```python
album = client.albums.get("<id>")

# Access typed attributes
print(album.name)           # str
print(album.release_date)   # str
print(album.total_tracks)   # int
print(album.artists)        # list[SimplifiedArtist]
print(album.images)         # list[Image]

# Models support forward compatibility
# Unknown fields from the API are preserved
```

## Development

Clone the repository:

```bash
git clone https://github.com/jonathan343/spotify-sdk.git
cd spotify-sdk
```

Install dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
uv run ruff format --check --preview .
```

### Sync/Async Architecture

The SDK uses an async-first architecture. Async code under `src/spotify_sdk/_async/` is the source of truth, and the sync code under `src/spotify_sdk/_sync/` is auto-generated using [unasync](https://github.com/python-trio/unasync). **Do not edit `_sync/` files directly.**

After making changes to `_async/` source or `tests/_async/`, regenerate the sync code:

```bash
uv run python scripts/run_unasync.py
```

To verify sync code is up to date (same check that runs in CI):

```bash
uv run python scripts/run_unasync.py --check
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
