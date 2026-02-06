# Authorization Code + Refresh Token Authentication

## Context

`spotify-sdk` already supports:

- Static bearer tokens (`access_token=...`).
- App-only OAuth via `AsyncClientCredentials` / `ClientCredentials`.

This document records the implemented Authorization Code + Refresh Token
approach for user-scoped endpoints (`/me`, library, follows, playback, playlist
writes). Design goals were:

- Fits the existing async-first + unasync architecture.
- Reuses current auth provider patterns (cache, retries, lock, env fallback).
- Avoids framework-specific behavior in core SDK.

## Goals

- Add a provider for Spotify Authorization Code flow.
- Automatically refresh expired access tokens with `refresh_token`.
- Keep the client integration unchanged (`auth_provider=...`).
- Preserve compatibility with existing `TokenCache` usage patterns.
- Keep sync API generated from async source.

## Non-goals

- PKCE in this iteration.
- Embedding browser/callback side effects directly in provider methods.
- Secure persistent token storage implementation in core SDK.

## Implemented Public API

### New provider classes

- `spotify_sdk.auth.AsyncAuthorizationCode` (canonical implementation).
- `spotify_sdk.auth.AuthorizationCode` (generated sync class).

### Constructor

```python
from spotify_sdk.auth import AsyncAuthorizationCode

auth = AsyncAuthorizationCode(
    client_id="...",
    client_secret="...",
    redirect_uri="http://127.0.0.1:8080/callback",
    scope=["user-read-private", "playlist-read-private"],
    refresh_token=None,  # optional bootstrap for returning users
    token_cache=None,    # defaults to InMemoryTokenCache
    timeout=30.0,
    max_retries=3,
    skew_seconds=30,
    http_client=None,
)
```

### Methods

```python
class AsyncAuthorizationCode:
    def get_authorization_url(
        self,
        *,
        state: str | None = None,
        scope: str | list[str] | tuple[str, ...] | None = None,
        show_dialog: bool = False,
    ) -> str: ...

    @staticmethod
    def parse_response_url(
        url: str,
        *,
        expected_state: str | None = None,
    ) -> str:  # returns authorization code
        ...

    async def exchange_code(self, code: str) -> TokenInfo: ...
    async def get_access_token(self) -> str: ...
    async def close(self) -> None: ...
```

### Local helper functions

```python
from spotify_sdk.auth import (
    AsyncAuthorizationCode,
    AuthorizationCode,
    async_authorize_local,
    authorize_local,
)

sync_auth = AuthorizationCode(scope="user-read-private")
sync_token = authorize_local(sync_auth)  # local loopback helper

async_auth = AsyncAuthorizationCode(scope="user-read-private")
async_token = await async_authorize_local(async_auth)
```

Both helpers are optional convenience layers for local/CLI flows. Core
provider methods remain explicit (`get_authorization_url`, `parse_response_url`,
`exchange_code`).

### Typical usage

```python
from spotify_sdk import AsyncSpotifyClient
from spotify_sdk.auth import AsyncAuthorizationCode

auth = AsyncAuthorizationCode(
    client_id="...",
    client_secret="...",
    redirect_uri="http://127.0.0.1:8080/callback",
    scope=["user-read-private", "playlist-read-private"],
)

state = "csrf-token-generated-by-app"
authorize_url = auth.get_authorization_url(state=state, show_dialog=True)

# App redirects user to authorize_url, then receives callback URL:
callback_url = "http://127.0.0.1:8080/callback?code=...&state=..."
code = auth.parse_response_url(callback_url, expected_state=state)
await auth.exchange_code(code)

async with AsyncSpotifyClient(auth_provider=auth) as client:
    # token is refreshed transparently when expired
    ...
```

## Provider Behavior

### Token lifecycle

1. `exchange_code(code)` sends `grant_type=authorization_code` request.
2. Response token is cached (`access_token`, `expires_at`, `refresh_token`).
3. `get_access_token()` serves cached token until near expiry.
4. On expiry, provider calls token endpoint with `grant_type=refresh_token`.
5. New token is cached. If refresh response omits `refresh_token`, keep the
   previous refresh token.

### Token endpoint requests

- Endpoint: `POST https://accounts.spotify.com/api/token`
- Headers:
    - `Authorization: Basic base64(client_id:client_secret)`
    - `Content-Type: application/x-www-form-urlencoded`
- Exchange payload:
    - `grant_type=authorization_code`
    - `code=<authorization_code>`
    - `redirect_uri=<registered_redirect_uri>`
- Refresh payload:
    - `grant_type=refresh_token`
    - `refresh_token=<refresh_token>`

### Authorization URL

- Endpoint: `https://accounts.spotify.com/authorize`
- Query params:
    - `response_type=code`
    - `client_id`
    - `redirect_uri`
    - `scope` (space-delimited, optional)
    - `state` (optional, recommended)
    - `show_dialog=true` (optional)

## Data Model and Cache

`TokenInfo` stores `access_token`, `expires_at`, `refresh_token`, and `scope`.

### `TokenInfo` shape

```python
@dataclass(frozen=True)
class TokenInfo:
    access_token: str
    expires_at: float
    refresh_token: str | None = None
    scope: str | None = None
```

Rationale:

- Keeps one cache protocol for all auth providers.
- Existing call sites remain valid because new fields are optional.
- Avoids introducing a second cache interface for a single field addition.

## Concurrency, Retry, and Errors

### Concurrency

- Keep the same lock pattern as `AsyncClientCredentials`:
    - `anyio.Lock` in async code.
    - `threading.Lock` in generated sync code.
- Use double-checked cache reads to avoid duplicate refresh calls.

### Retry

- Reuse current backoff strategy and constants:
    - Retry connection/timeouts and 5xx responses.
    - Do not retry 4xx OAuth errors except explicit caller retry.

### Error mapping

- OAuth failures (`invalid_grant`, `invalid_client`, state mismatch, missing
  code) map to `AuthenticationError`.
- Unexpected transport failures map to `SpotifyError` consistent with existing
  auth providers.

## Integration with Existing SDK

### No client constructor changes required

The existing client API already supports custom providers:

```python
AsyncSpotifyClient(auth_provider=auth)
SpotifyClient(auth_provider=auth)
```

No changes required to `AsyncBaseClient` / `BaseClient` contract.

### Implementation touchpoints

- `src/spotify_sdk/_async/auth/__init__.py`:
    - Add `AsyncAuthorizationCode`.
    - Extend `TokenInfo`.
    - Add `ENV_REDIRECT_URI` constant.
- `src/spotify_sdk/auth/__init__.py`:
    - Export `AsyncAuthorizationCode` and generated `AuthorizationCode`.
- `scripts/run_unasync.py`:
    - Add replacement mapping:
      - `"AsyncAuthorizationCode": "AuthorizationCode"`
- Tests:
    - Add `tests/_async/test_auth_authorization_code.py`.
    - Regenerate sync tests via `scripts/run_unasync.py`.

## Deviations from Spotipy (Intentional)

Compared with `spotipy.SpotifyOAuth`, this design keeps provider methods
explicit and side-effect free by default:

- Provider classes handle token mechanics (URL generation, code exchange,
  refresh) without forcing browser or prompt behavior.
- Local browser/callback automation is available via opt-in helper functions
  (`authorize_local` and `async_authorize_local`).

Why:

- Keeps SDK deterministic and side-effect free in libraries/services.
- Works cleanly in web backends, CLIs, notebooks, and serverless contexts.
- Avoids coupling auth provider to UI/transport concerns.
- Preserves convenience for local development through helper APIs.

## Security and Operational Notes

- Strongly recommend using `state` and validating it in `parse_response_url`.
- Require exact redirect URI matching with Spotify app settings.
- Do not log tokens or authorization codes.
- In-memory cache is default; production apps should provide secure persistent
  cache implementations if session continuity is needed.

## Testing Plan

- URL generation:
    - required params
    - optional `scope`, `state`, `show_dialog`
- Callback parsing:
    - success path
    - missing code
    - `error=` responses
    - state mismatch
- Token exchange:
    - successful authorization code exchange
    - malformed token response handling
- Refresh:
    - refresh on expiry
    - preserve old refresh token when omitted in refresh response
    - error mapping for token endpoint failures
- Concurrency:
    - concurrent expired-token requests result in one refresh call
- Environment fallback:
    - `client_id`, `client_secret`, and `redirect_uri` resolution

## References

- [Spotify Authorization concepts](https://developer.spotify.com/documentation/web-api/concepts/authorization)
- [Spotify Authorization Code tutorial](https://developer.spotify.com/documentation/web-api/tutorials/code-flow)
- [Spotify Refreshing Tokens tutorial](https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens)
