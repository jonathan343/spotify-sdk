# Changelog

## v0.9.0

### Features
* Added `authorize_local()` instance methods on `AuthorizationCode` and `AsyncAuthorizationCode` in `spotify_sdk.auth` so local loopback auth can be started directly from the auth object (`auth.authorize_local()` / `await auth.authorize_local()`) while keeping function helpers for backward compatibility. ([#63](https://github.com/jonathan343/spotify-sdk/pull/63))
* Added full playlist mutation API support (`create`, `change_details`, `reorder_or_replace_items`, `add_items`, `remove_items`, and `upload_cover_image`). ([#60](https://github.com/jonathan343/spotify-sdk/pull/60))

## v0.8.0

### Features
* Add `AsyncShowService`/`ShowService` with `get`, `get_episodes`, and `get_save` operations; add show/episode models, wire `client.shows`, and include async/sync test coverage. ([#52](https://github.com/jonathan343/spotify-sdk/pull/52))
* Add `AsyncEpisodeService`/`EpisodeService` with `get` and `get_saved` operations; add `SavedEpisode` model support, wire `client.episodes`, and include async/sync unit + integration coverage. ([#53](https://github.com/jonathan343/spotify-sdk/pull/53))
* Add `AsyncSearchService`/`SearchService` with typed catalog search support across albums, artists, playlists, tracks, shows, episodes, and audiobooks. ([#55](https://github.com/jonathan343/spotify-sdk/pull/55))

## v0.7.0

### Features
* Added support for user saved album library endpoints with `albums.get_saved(...)` and `albums.check_saved(...)`, now enabled by authorization code flow with scopes. Also introduced the `SavedAlbum` model and documented the new album APIs. ([#48](https://github.com/jonathan343/spotify-sdk/pull/48))
* Add `AsyncLibraryService`/`LibraryService` for URI-based user library save/remove/contains operations, with client wiring, docs, and unit/integration test coverage. ([#50](https://github.com/jonathan343/spotify-sdk/pull/50))

## v0.6.0

### Features
* Add [Authorization Code](https://developer.spotify.com/documentation/web-api/tutorials/code-flow) + refresh-token auth with local loopback helpers, file token cache, and async helper loop-safety fixes; update auth docs/design for consistent setup and usage guidance. ([#43](https://github.com/jonathan343/spotify-sdk/pull/43))
* Add `AsyncUserService`/`UserService` with user APIs for current profile, top artists/tracks, playlist follow/unfollow, followed artists, artist/user follow/unfollow, and follow-status checks. ([#44](https://github.com/jonathan343/spotify-sdk/pull/44))

### Documentation
* Update docs for the new users service (quickstart + reference pages). ([#44](https://github.com/jonathan343/spotify-sdk/pull/44))

## v0.5.0

### Features
* Add audiobook models and services (sync + async), including chapter pagination support and tests. ([#38](https://github.com/jonathan343/spotify-sdk/pull/38))
* Add chapter support with new Chapter model and chapter service methods for getting a chapter and fetching multiple chapters. ([#39](https://github.com/jonathan343/spotify-sdk/pull/39))

### Documentation
* Add documentation for the new audiobooks service. ([#38](https://github.com/jonathan343/spotify-sdk/pull/38))
* Add documentation for the new chapters service. ([#39](https://github.com/jonathan343/spotify-sdk/pull/39))

## v0.4.0

### Features
* Add support for Spotify's [Client Credentials Flow](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow) with public auth helpers, token caching, and env var support. ([#36](https://github.com/jonathan343/spotify-sdk/pull/36))

### Documentation
* Document client credentials usage, auth helpers, env vars, and limitations across quickstart, client reference, and a new auth reference page. ([#36](https://github.com/jonathan343/spotify-sdk/pull/36))

## v0.3.0

### Breaking Changes
* Renamed `album_id` and `track_id` parameters to `id`, and `album_ids` and `track_ids` to `ids` in `AlbumService` and `TrackService` methods for consistency with the Spotify API. ([#30](https://github.com/jonathan343/spotify-sdk/pull/30))

### Features
* Added `ArtistService` (sync) and `AsyncArtistService` (async) with methods for fetching an artist by ID, fetching multiple artists (up to 50), listing an artist's albums, and getting their top tracks. ([#25](https://github.com/jonathan343/spotify-sdk/pull/25))
* Add `PlaylistService` (sync) and `AsyncPlaylistService` (async) with methods for fetching a playlist by ID, getting playlist items, listing the current user's playlists, listing a user's playlists, and getting playlist cover images. ([#31](https://github.com/jonathan343/spotify-sdk/pull/31))

### Enhancements
* Expose package version via `spotify_sdk.__version__`.
* Enable pydocstyle linting with Google convention for consistent docstring formatting. ([#32](https://github.com/jonathan343/spotify-sdk/pull/32))

## v0.2.0

### Breaking Changes
* Replace dual-mode `SpotifyClient` with separate `AsyncSpotifyClient` and `SpotifyClient` classes; async methods no longer use `_async` suffix. ([#21](https://github.com/jonathan343/spotify-sdk/pull/21))

### Enhancements
* Async client now supports trio in addition to asyncio as a backend. ([#21](https://github.com/jonathan343/spotify-sdk/pull/21))

## v0.1.1

### Enhancements
* Add `get_new_releases` and `get_new_releases_async` methods to `AlbumService` for retrieving new album releases from Spotify's Browse API ([#13](https://github.com/jonathan343/spotify-sdk/pull/13)).
* Add `TrackService` with `get`, `get_several`, and async variants for retrieving tracks from the Spotify API ([#14](https://github.com/jonathan343/spotify-sdk/pull/14)).

## v0.1.0

### Features
* Add `Artist` and `SimplifiedArtist` models with common models (`Image`, `ExternalUrls`, `Followers`) and forward-compatible base `SpotifyModel` ([#3](https://github.com/jonathan343/spotify-sdk/pull/3)).
* Add `Album`, `SimplifiedAlbum`, `Track`, `SimplifiedTrack` models with `Page[T]` generic for pagination and additional common models (`ExternalIds`, `Copyright`, `LinkedFrom`, `Restriction`) ([#7](https://github.com/jonathan343/spotify-sdk/pull/7)).
* Add `SpotifyClient` with dual sync/async HTTP support, `AlbumService` with full CRUD operations (`get`, `get_several`, `get_tracks`), comprehensive exception hierarchy (`SpotifyError`, `AuthenticationError`, `BadRequestError`, `ForbiddenError`, `NotFoundError`, `RateLimitError`, `ServerError`), automatic retry with exponential backoff for rate limits (429) and server errors (5xx), and input validation ([#8](https://github.com/jonathan343/spotify-sdk/pull/8)).

## v0.0.0a1

### Features
* Initial version of spotify-sdk.
