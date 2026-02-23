---
icon: lucide/house
---

# Spotify SDK for Python

<div align="center">
  <img width="250" src="/images/logo.png" alt="Spotify SDK logo" />
</div>

[![PyPI version](https://img.shields.io/pypi/v/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Actions status](https://github.com/jonathan343/spotify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/jonathan343/spotify-sdk/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/jonathan343/spotify-sdk/blob/main/LICENSE)

`spotify-sdk` is a Python client for the
[Spotify Web API](https://developer.spotify.com/documentation/web-api).
It provides sync and async interfaces with type-safe responses, so you
can build apps against Spotify without managing raw HTTP or JSON.

!!! note "Community Project"
    This is an independent, community-developed library and is not affiliated with or endorsed by Spotify.

[Quickstart](quickstart.md){ .md-button .md-button--primary }
[Installation](installation.md){ .md-button }
[API Reference](reference/index.md){ .md-button }
[View on GitHub](https://github.com/jonathan343/spotify-sdk){ .md-button }

---

## Features

- **Type-safe models**: Pydantic models with full type hints for every response
- **Sync and async clients**: `SpotifyClient` and `AsyncSpotifyClient` with identical APIs
- **Automatic retries**: Exponential backoff with jitter for rate limits, server errors, and timeouts
- **Auth helpers**: Client credentials, authorization code, and local browser-based flows
- **Token caching**: Built-in in-memory cache with a pluggable `TokenCache` interface
- **Context managers**: `with` and `async with` support for clean resource cleanup

---

## Start in 60 Seconds

=== "Sync"

    ```python
    from spotify_sdk import SpotifyClient

    with SpotifyClient(access_token="your-access-token") as client:
        album = client.albums.get("<spotify-album-id>")
        print(album.name)
        print(album.artists[0].name)
    ```

=== "Async"

    ```python
    import asyncio
    from spotify_sdk import AsyncSpotifyClient

    async def main() -> None:
        async with AsyncSpotifyClient(access_token="your-access-token") as client:
            album = await client.albums.get("<spotify-album-id>")
            print(album.name)
            print(album.artists[0].name)

    asyncio.run(main())
    ```

[:octicons-arrow-right-24: See the full quickstart](quickstart.md)

---

<div class="grid cards" markdown>

- __Quickstart__

    ---

    Install, configure auth, and make your first API call in minutes.

    [:octicons-arrow-right-24: Start here](quickstart.md)

- __Authentication__

    ---

    Client credentials, authorization code, `authorize_local`, and pluggable
    token caching.

    [:octicons-arrow-right-24: Auth guide](reference/auth.md)

- __Services__

    ---

    Albums, Artists, Audiobooks, Chapters, Episodes, Library, Playlists,
    Search, Shows, Tracks, and Users.

    [:octicons-arrow-right-24: Service reference](reference/services/index.md)

- __Installation__

    ---

    Install with `uv` or `pip` and verify your setup. Requires Python 3.10+.

    [:octicons-arrow-right-24: Install](installation.md)

- __Error Handling__

    ---

    Handle `RateLimitError`, `AuthenticationError`, and other SDK exceptions.

    [:octicons-arrow-right-24: Exceptions](quickstart.md#error-handling)

- __Clients & Models__

    ---

    Full reference for client configuration and Pydantic response models.

    [:octicons-arrow-right-24: Explore reference](reference/index.md)

</div>
