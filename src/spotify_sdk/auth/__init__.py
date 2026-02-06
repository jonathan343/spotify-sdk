"""Public auth exports."""

from __future__ import annotations

from functools import partial
from typing import Callable

from anyio import to_thread

from .._async.auth import (
    AsyncAuthorizationCode,
    AsyncAuthProvider,
    AsyncClientCredentials,
    FileTokenCache,
    InMemoryTokenCache,
    TokenCache,
    TokenInfo,
)
from .._async.auth import (
    authorize_local as _authorize_local_async_impl,
)
from .._sync.auth import AuthorizationCode, ClientCredentials, authorize_local


async def async_authorize_local(
    auth: AsyncAuthorizationCode,
    *,
    state: str | None = None,
    show_dialog: bool = False,
    timeout: float = 300.0,  # noqa: ASYNC109
    open_browser: bool = True,
    authorization_url_handler: Callable[[str], None] | None = None,
) -> TokenInfo:
    """Run local auth flow from async code without blocking the event loop."""
    runner = partial(
        _authorize_local_async_impl,
        auth,
        state=state,
        show_dialog=show_dialog,
        timeout=timeout,
        open_browser=open_browser,
        authorization_url_handler=authorization_url_handler,
    )
    return await to_thread.run_sync(runner)


__all__ = [
    "AsyncAuthorizationCode",
    "async_authorize_local",
    "AsyncAuthProvider",
    "AsyncClientCredentials",
    "AuthorizationCode",
    "ClientCredentials",
    "FileTokenCache",
    "InMemoryTokenCache",
    "TokenCache",
    "TokenInfo",
    "authorize_local",
]
