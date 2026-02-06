---
icon: lucide/lock
---

# Auth

Auth helpers live in `spotify_sdk.auth`. They power client credentials,
authorization code auth, and custom providers.

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

### Limitations

Client credentials tokens cannot access user endpoints (for example, `/me/*`).

## Authorization Code

Use authorization code flow for user-scoped endpoints. The provider generates
an authorize URL, exchanges a callback code for tokens, and refreshes access
tokens automatically.

=== "Sync"

    ```python
    from spotify_sdk.auth import AuthorizationCode

    auth = AuthorizationCode(
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="http://127.0.0.1:8080/callback",
        scope=["user-read-private", "playlist-read-private"],
    )

    state = "csrf-token-generated-by-app"
    url = auth.get_authorization_url(state=state, show_dialog=True)
    # Redirect user to `url` and capture callback URL in your app.
    code = auth.parse_response_url(
        "http://127.0.0.1:8080/callback?code=...&state=...",
        expected_state=state,
    )
    auth.exchange_code(code)
    ```

=== "Async"

    ```python
    from spotify_sdk.auth import AsyncAuthorizationCode

    auth = AsyncAuthorizationCode(
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="http://127.0.0.1:8080/callback",
        scope=["user-read-private", "playlist-read-private"],
    )

    state = "csrf-token-generated-by-app"
    url = auth.get_authorization_url(state=state, show_dialog=True)
    # Redirect user to `url` and capture callback URL in your app.
    code = auth.parse_response_url(
        "http://127.0.0.1:8080/callback?code=...&state=...",
        expected_state=state,
    )
    await auth.exchange_code(code)
    ```

### Environment Variables

If `client_id`, `client_secret`, or `redirect_uri` are omitted, the SDK reads:

- `SPOTIFY_SDK_CLIENT_ID`
- `SPOTIFY_SDK_CLIENT_SECRET`
- `SPOTIFY_SDK_REDIRECT_URI`

Explicit arguments override environment variables.

### Local Dev Helper (No Copy/Paste)

For local CLI workflows, use `authorize_local(...)` to open the browser,
capture the loopback callback automatically, and exchange the code.

```python
from spotify_sdk.auth import AuthorizationCode, authorize_local

auth = AuthorizationCode(
    scope="user-library-read",
)

token_info = authorize_local(auth)
print(token_info.refresh_token)
```

`authorize_local` requires a loopback redirect URI (`http://127.0.0.1:PORT/...`
or `http://localhost:PORT/...`).

For async applications (notebooks, async CLIs, web handlers), use
`async_authorize_local(...)`:

```python
from spotify_sdk.auth import AsyncAuthorizationCode, async_authorize_local

auth = AsyncAuthorizationCode(scope="user-library-read")
token_info = await async_authorize_local(auth)
print(token_info.refresh_token)
```

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

### Built-in File Cache

Use `FileTokenCache` to persist tokens between runs.

```python
from spotify_sdk.auth import AuthorizationCode, FileTokenCache

cache = FileTokenCache(path=".cache/spotify-sdk/token.json")
auth = AuthorizationCode(
    scope="user-library-read",
    token_cache=cache,
)
```

### TokenInfo

`TokenInfo` is a simple container used by caches:

```python
from spotify_sdk.auth import TokenInfo

token = TokenInfo(
    access_token="...",
    expires_at=1700000000.0,
    refresh_token="...",
    scope="user-read-private playlist-read-private",
)
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
