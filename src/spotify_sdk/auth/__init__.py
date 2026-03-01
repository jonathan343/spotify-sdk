"""Public auth exports."""

from __future__ import annotations

from functools import partial
from typing import Callable

from anyio import to_thread

from .._async.auth import (
    AsyncAuthorizationCode as _AsyncAuthorizationCode,
)
from .._async.auth import (
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
from .._sync.auth import (
    AuthorizationCode as _AuthorizationCode,
)
from .._sync.auth import (
    ClientCredentials,
)
from .._sync.auth import (
    TokenInfo as _SyncTokenInfo,
)
from .._sync.auth import (
    authorize_local as _authorize_local_sync_impl,
)


class AsyncAuthorizationCode(_AsyncAuthorizationCode):
    """Authorization code provider with async local helper method."""

    async def authorize_local(
        self,
        *,
        state: str | None = None,
        show_dialog: bool = False,
        timeout: float = 300.0,  # noqa: ASYNC109
        open_browser: bool = True,
        authorization_url_handler: Callable[[str], None] | None = None,
    ) -> TokenInfo:
        """Run loopback local auth flow without blocking the event loop."""
        return await async_authorize_local(
            self,
            state=state,
            show_dialog=show_dialog,
            timeout=timeout,
            open_browser=open_browser,
            authorization_url_handler=authorization_url_handler,
        )


class AuthorizationCode(_AuthorizationCode):
    """Authorization code provider with local helper method."""

    def authorize_local(
        self,
        *,
        state: str | None = None,
        show_dialog: bool = False,
        timeout: float = 300.0,
        open_browser: bool = True,
        authorization_url_handler: Callable[[str], None] | None = None,
    ) -> _SyncTokenInfo:
        """Run loopback local auth flow and exchange the callback code."""
        return _authorize_local_sync_impl(
            self,
            state=state,
            show_dialog=show_dialog,
            timeout=timeout,
            open_browser=open_browser,
            authorization_url_handler=authorization_url_handler,
        )


async def async_authorize_local(
    auth: _AsyncAuthorizationCode,
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


def authorize_local(
    auth: _AuthorizationCode,
    *,
    state: str | None = None,
    show_dialog: bool = False,
    timeout: float = 300.0,
    open_browser: bool = True,
    authorization_url_handler: Callable[[str], None] | None = None,
) -> _SyncTokenInfo:
    """Backward-compatible function helper for sync local auth flow."""
    return _authorize_local_sync_impl(
        auth,
        state=state,
        show_dialog=show_dialog,
        timeout=timeout,
        open_browser=open_browser,
        authorization_url_handler=authorization_url_handler,
    )


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
