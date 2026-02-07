# API Reference

This section documents the public SDK surface area. Sync and async
implementations share the same service names and method signatures, so the
reference is grouped by service with code tabs for the sync and async styles.

!!! note "Sync and async docs together"
    The SDK is async-first internally, and the sync API is generated from it.
    To avoid duplicate pages and keep examples aligned, the reference keeps
    both variants on the same page using tabs. If a method ever diverges, the
    sync or async tab will call it out explicitly.

<div class="grid cards" markdown>

- __Clients__

    ---

    Construction, lifecycle, and configuration for the main entry points.

    [:octicons-arrow-right-24: Clients](clients.md)

- __Auth__

    ---

    Client credentials and auth provider utilities.

    [:octicons-arrow-right-24: Auth](auth.md)

- __Services__

    ---

    Albums, audiobooks, chapters, artists, playlists, tracks, and users operations.

    [:octicons-arrow-right-24: Services](services/index.md)

- __Models__

    ---

    Pydantic models for Spotify API responses.

    [:octicons-arrow-right-24: Models](models.md)

</div>
