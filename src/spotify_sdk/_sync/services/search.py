"""Search service for Spotify API."""

from __future__ import annotations

from typing import Literal, get_args

from ...models import SearchResult
from .._base_service import BaseService

SearchType = Literal[
    "album",
    "artist",
    "playlist",
    "track",
    "show",
    "episode",
    "audiobook",
]
IncludeExternal = Literal["audio"]
VALID_SEARCH_TYPES = set(get_args(SearchType))


class SearchService(BaseService):
    """Operations for searching Spotify catalog content."""

    def search(
        self,
        q: str,
        types: list[SearchType],
        market: str | None = None,
        limit: int = 5,
        offset: int = 0,
        include_external: IncludeExternal | None = None,
    ) -> SearchResult:
        """Search for items in the Spotify catalog.

        Args:
            q: Search query keywords and filters.
            types: Resource types to search.
            market: An ISO 3166-1 alpha-2 country code.
            limit: Maximum number of results per type (0-50, default 5).
            offset: Index of the first result to return.
            include_external: Whether to include externally hosted audio.

        Returns:
            Search results grouped by requested type.

        Raises:
            ValueError: If q is empty, types is empty, or types contain
                unsupported values.
        """
        if not q:
            raise ValueError("q cannot be empty")
        if not types:
            raise ValueError("types cannot be empty")

        invalid = set(types) - VALID_SEARCH_TYPES
        if invalid:
            raise ValueError(
                f"Invalid types: {invalid}. Valid values: {VALID_SEARCH_TYPES}"
            )

        params: dict[str, str | int] = {
            "q": q,
            "type": ",".join(types),
            "limit": limit,
            "offset": offset,
        }
        if market is not None:
            params["market"] = market
        if include_external is not None:
            params["include_external"] = include_external

        data = self._get("/search", params=params)
        return SearchResult.model_validate(data)
