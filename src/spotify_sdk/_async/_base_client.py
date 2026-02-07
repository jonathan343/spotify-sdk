"""Base HTTP client for Spotify API communication."""

from __future__ import annotations

import random
from typing import Any, TypeAlias

import anyio
import httpx

from ..exceptions import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SpotifyError,
)
from .auth import AsyncAuthProvider

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = (
    JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
)


class AsyncBaseClient:
    """Low-level HTTP client for Spotify API."""

    BASE_URL = "https://api.spotify.com/v1"

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 0.5
    MAX_BACKOFF = 8.0
    BACKOFF_MULTIPLIER = 2

    def __init__(
        self,
        access_token: str | None = None,
        auth_provider: AsyncAuthProvider | None = None,
        timeout: float = 30.0,
        max_retries: int | None = None,
    ) -> None:
        """Initialize the base client.

        Args:
            access_token: Spotify API access token.
            auth_provider: Auth provider for dynamic access tokens.
            timeout: Default request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        if access_token and auth_provider:
            raise ValueError(
                "Provide only one of access_token or auth_provider."
            )
        if not access_token and not auth_provider:
            raise ValueError(
                "Either access_token or auth_provider must be provided."
            )

        self._access_token = access_token
        self._auth_provider = auth_provider
        self._timeout = timeout
        self._max_retries = (
            max_retries if max_retries is not None else self.MAX_RETRIES
        )
        self._client: httpx.AsyncClient | None = None

    @property
    def _http_client(self) -> httpx.AsyncClient:
        """Lazily initialize and return the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=self._timeout,
            )
        return self._client

    def _default_headers(self, access_token: str) -> dict[str, str]:
        """Return default headers for all requests."""
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        if self._auth_provider:
            return await self._auth_provider.get_access_token()
        raise SpotifyError("No access token available.")

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,  # noqa: ASYNC109
        max_retries: int | None = None,
    ) -> JSONValue:
        """Make an HTTP request to the Spotify API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API endpoint path.
            params: Query parameters.
            json: JSON body for POST/PUT requests.
            timeout: Request timeout override.
            max_retries: Max retries override.

        Returns:
            Parsed JSON response.

        Raises:
            SpotifyError: On API errors.
        """
        retries = max_retries if max_retries is not None else self._max_retries
        last_exception: Exception | None = None

        for attempt in range(retries + 1):
            try:
                access_token = await self._get_access_token()
                response = await self._http_client.request(
                    method=method,
                    url=path,
                    params=self._clean_params(params),
                    json=json,
                    timeout=timeout,
                    headers=self._default_headers(access_token),
                )
                return self._handle_response(response)

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < retries:
                    await anyio.sleep(self._calculate_backoff(attempt))
                    continue
                raise SpotifyError(f"Connection error: {e}") from e

            except RateLimitError as e:
                last_exception = e
                if attempt < retries:
                    sleep_time = e.retry_after or self._calculate_backoff(
                        attempt
                    )
                    await anyio.sleep(sleep_time)
                    continue
                raise

            except ServerError as e:
                last_exception = e
                if attempt < retries:
                    await anyio.sleep(self._calculate_backoff(attempt))
                    continue
                raise

        raise last_exception or SpotifyError("Request failed after retries")

    def _handle_response(self, response: httpx.Response) -> JSONValue:
        """Process HTTP response and raise appropriate exceptions."""
        if response.status_code == 204:
            return {}

        try:
            data = response.json()
        except Exception:
            data = {}

        if response.is_success:
            return data

        error_message = self._extract_error_message(data)

        if response.status_code == 400:
            raise BadRequestError(error_message, response.status_code, data)
        elif response.status_code == 401:
            raise AuthenticationError(
                error_message, response.status_code, data
            )
        elif response.status_code == 403:
            raise ForbiddenError(error_message, response.status_code, data)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response.status_code, data)
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            raise RateLimitError(
                error_message,
                response.status_code,
                data,
                retry_after=retry_after,
            )
        elif response.status_code >= 500:
            raise ServerError(error_message, response.status_code, data)
        else:
            raise SpotifyError(error_message, response.status_code, data)

    def _extract_error_message(self, data: JSONValue) -> str:
        """Extract error message from Spotify error response."""
        if isinstance(data, dict) and "error" in data:
            error = data["error"]
            if isinstance(error, dict):
                message = error.get("message", "Unknown error")
                return str(message)
            return str(error)
        return "Unknown error"

    def _clean_params(
        self, params: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Remove None values from query parameters."""
        if params is None:
            return None
        return {k: v for k, v in params.items() if v is not None}

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time with jitter."""
        backoff = min(
            self.INITIAL_BACKOFF * (self.BACKOFF_MULTIPLIER**attempt),
            self.MAX_BACKOFF,
        )
        # Add jitter (0.5 to 1.0 multiplier)
        return backoff * (0.5 + random.random() * 0.5)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._auth_provider and hasattr(self._auth_provider, "close"):
            await self._auth_provider.close()

    async def __aenter__(self) -> "AsyncBaseClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
