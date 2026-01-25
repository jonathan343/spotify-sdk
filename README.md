# Spotify SDK for Python

[![PyPI version](https://img.shields.io/pypi/v/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Actions status](https://github.com/jonathan343/spotify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/jonathan343/spotify-sdk/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Python SDK for the [Spotify Web API](https://developer.spotify.com/documentation/web-api).

> **Note**: This is an independent, community-developed library and is not affiliated with or endorsed by Spotify.

## Features

- **Type-safe**: Full type hints with Pydantic models for all API responses
- **Sync and async**: Both synchronous and asynchronous client support
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

The SDK currently supports [access token](https://developer.spotify.com/documentation/web-api/concepts/access-token) authentication. You'll need to obtain an access token through Spotify's authorization flows before using the SDK.

```python
client = SpotifyClient(access_token="your-access-token")
```

Additional authentication methods are planned for future releases.

## Quick Start

```python
from spotify_sdk import SpotifyClient

client = SpotifyClient(access_token="your-access-token")

# Get an album
album = client.albums.get("4aawyAB9vmqN3uQ7FjRGTy")
print(album.name)  # "Global Warming"

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
from spotify_sdk import SpotifyClient

async def main():
    async with SpotifyClient(access_token="your-access-token") as client:
        album = await client.albums.get_async("4aawyAB9vmqN3uQ7FjRGTy")
        print(album.name)

        # Fetch multiple albums concurrently
        albums = await client.albums.get_several_async([
            "4aawyAB9vmqN3uQ7FjRGTy",
            "2noRn2Aes5aoNVsU6iWThc",
        ])
        for album in albums:
            print(album.name)

asyncio.run(main())
```

## Services

### Albums

```python
# Get a single album
album = client.albums.get("album_id")
album = client.albums.get("album_id", market="US")

# Get multiple albums (up to 20)
albums = client.albums.get_several(["album_id_1", "album_id_2"])

# Get album tracks with pagination
tracks = client.albums.get_tracks("album_id", limit=10, offset=0)
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
album = client.albums.get("album_id")

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
uv sync --group lint --group test
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

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
