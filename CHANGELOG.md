# Changelog

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
