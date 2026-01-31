---
icon: lucide/house
---

# Welcome

<div align="center">
  <img width="250" src="/images/logo.png" />
</div>

[![PyPI version](https://img.shields.io/pypi/v/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotify-sdk.svg)](https://pypi.org/project/spotify-sdk/)
[![Actions status](https://github.com/jonathan343/spotify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/jonathan343/spotify-sdk/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


`spotify-sdk` is a modern, type-safe Python SDK for the [Spotify Web API](https://developer.spotify.com/documentation/web-api). Fetch albums, artists, tracks, and more with both sync and async clients.

[Get Started](quickstart.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/jonathan343/spotify-sdk){ .md-button }

---

<div class="grid cards" markdown>

- __Installation__

    ---

    Install with pip or uv and start building in seconds.

    [:octicons-arrow-right-24: Install](installation.md)

- __Quickstart__

    ---

    Learn the basics with sync and async examples.

    [:octicons-arrow-right-24: Get started](quickstart.md)

- __Configuration__

    ---

    Customize timeouts, retries, and client behavior.

    [:octicons-arrow-right-24: Configure](quickstart.md#configuration)

- __Error Handling__

    ---

    Handle rate limits, auth errors, and API failures gracefully.

    [:octicons-arrow-right-24: Learn more](quickstart.md#error-handling)

</div>

---

## Features

- **Type-safe** - Full type hints with Pydantic models for all API responses
- **Sync and async** - Dedicated `SpotifyClient` and `AsyncSpotifyClient` classes
- **Automatic retries** - Exponential backoff with jitter for rate limits and transient errors
- **Context managers** - Clean resource management with `with` and `async with` support

---

## Quick Example

```python
from spotify_sdk import SpotifyClient

with SpotifyClient(access_token="your-access-token") as client:
    album = client.albums.get("7ycBtnsMtyVbbwTfJwRjSP")
    print(f"{album.name} by {album.artists[0].name}")  # (1)!
```

1. Output: `To Pimp A Butterfly by Kendrick Lamar`

[:octicons-arrow-right-24: See more examples](quickstart.md)

---

!!! note "Community Project"
    This is an independent, community-developed library and is not affiliated with or endorsed by Spotify.
