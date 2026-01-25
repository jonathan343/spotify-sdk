# Changelog

## v0.1.0

### Features
* Add `Artist` and `SimplifiedArtist` models with common models (`Image`, `ExternalUrls`, `Followers`) and forward-compatible base `SpotifyModel` ([#3](https://github.com/jonathan343/spotify-sdk/pull/3)).
* Add `Album`, `SimplifiedAlbum`, `Track`, `SimplifiedTrack` models with `Page[T]` generic for pagination and additional common models (`ExternalIds`, `Copyright`, `LinkedFrom`, `Restriction`) ([#7](https://github.com/jonathan343/spotify-sdk/pull/7)).
* Add `SpotifyClient` with dual sync/async HTTP support, `AlbumService` with full CRUD operations (`get`, `get_several`, `get_tracks`), comprehensive exception hierarchy (`SpotifyError`, `AuthenticationError`, `BadRequestError`, `ForbiddenError`, `NotFoundError`, `RateLimitError`, `ServerError`), automatic retry with exponential backoff for rate limits (429) and server errors (5xx), and input validation ([#8](https://github.com/jonathan343/spotify-sdk/pull/8)).

## v0.0.0a1

### Features
* Initial version of spotify-sdk.
