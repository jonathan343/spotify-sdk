---
icon: lucide/lock
---

# Auth

Auth helpers live in `spotify_sdk.auth`. They power client credentials and
custom auth providers.

## Client Credentials

Use client credentials to let the SDK fetch and refresh access tokens.

=== "Sync"

    ```python
    from spotify_sdk.auth import ClientCredentials

    auth = ClientCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    ```

=== "Async"

    ```python
    from spotify_sdk.auth import AsyncClientCredentials

    auth = AsyncClientCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    ```

### Environment Variables

If `client_id` or `client_secret` are omitted, the SDK reads:

- `SPOTIFY_SDK_CLIENT_ID`
- `SPOTIFY_SDK_CLIENT_SECRET`

Explicit arguments override environment variables.

### Limitations

Client credentials tokens cannot access user endpoints (for example, `/me/*`).

## Token Cache

The client credentials provider caches tokens in memory by default. You can
pass a custom cache implementation that follows this interface:

```python
from typing import Protocol

from spotify_sdk.auth import TokenInfo


class TokenCache(Protocol):
    def get(self) -> TokenInfo | None:
        ...

    def set(self, token: TokenInfo) -> None:
        ...
```

### TokenInfo

`TokenInfo` is a simple container used by caches:

```python
from spotify_sdk.auth import TokenInfo

token = TokenInfo(access_token="...", expires_at=1700000000.0)
```

## Auth Providers

You can supply custom providers to clients via `auth_provider=...`. Providers
need a `get_access_token()` method and an optional `close()`.

=== "Sync"

    ```python
    from typing import Protocol

    class AuthProvider(Protocol):
        def get_access_token(self) -> str:
            ...

        def close(self) -> None:
            ...
    ```

=== "Async"

    ```python
    from typing import Protocol

    class AsyncAuthProvider(Protocol):
        async def get_access_token(self) -> str:
            ...

        async def close(self) -> None:
            ...
    ```
