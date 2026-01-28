---
title: Async-First Architecture with Unasync Code Generation
status: implemented
created: 2025-01-25
implemented: 2025-01-28
version: 0.2.0
pr: "https://github.com/jonathan343/spotify-sdk/pull/21"
---

# Async-First Architecture with Unasync Code Generation

## Motivation

The SDK previously combined sync and async support in a single `SpotifyClient`
class using a dual-method pattern. Every public operation existed twice: a sync
version (`get`, `get_several`) and an async version (`get_async`,
`get_several_async`). The same was true at the infrastructure layer —
`BaseClient.request()` and `BaseClient.request_async()` contained identical
retry logic, differing only in `await` and `anyio.sleep` vs `time.sleep`.

This duplication created concrete problems:

- **Every bug fix must be applied twice.** A change to retry logic in `request()`
  must be manually mirrored in `request_async()`. A missed update silently
  creates behavioral divergence.
- **Every new service method is 2x the work.** Adding a method to `AlbumService`
  requires writing the sync body, copy-pasting it, adding `async`/`await`, and
  renaming helpers to their `_async` variants.
- **Tests double.** Each service test class contains paired sync and async tests
  with near-identical bodies.
- **The API is noisy.** Async users must remember to call `get_async` instead of
  `get`, and `aclose` instead of `close`. The `_async` suffix adds no information
  that an `AsyncSpotifyClient` class name wouldn't already convey.

For reference, this is the same problem discussed in Seth Larson's
[Designing libraries for async and sync I/O](https://sethmlarson.dev/designing-libraries-for-async-and-sync-io),
and the approach taken by `httpcore`, `httpx`, and `urllib3`.

## Approach

**Async is the single source of truth.** All I/O-bearing code is written once, as
async Python. A code generation script (`scripts/run_unasync.py`) mechanically
transforms the async source into a sync variant by stripping `async`/`await` and
swapping async-specific constructs for their sync equivalents. The generated sync
code is committed to the repository so that it is visible to IDEs, type checkers,
and reviewers.

We use the [`unasync`](https://github.com/python-trio/unasync) library with a
thin wrapper script that configures project-specific rules and runs
post-processing.

## Prior Art: elasticsearch-py

The [`elasticsearch-py`](https://github.com/elastic/elasticsearch-py) SDK uses
this exact pattern at significant scale (~50 async client namespace modules, a DSL
layer, vectorstore helpers, and generated tests). Key findings from their
implementation that informed this design:

1. **They use the `unasync` library, not a custom script.** The `unasync` package
   handles standard `async def` → `def` / `await` → removal / `async with` → `with`
   transformations out of the box. Project-specific class renames (e.g.
   `AsyncElasticsearch` → `Elasticsearch`) are handled via the
   `additional_replacements` dict on `unasync.Rule`. This is far simpler than
   writing a custom tokenizer — their script (`utils/run-unasync.py`) is ~120
   lines including boilerplate.

2. **Post-processing is still needed.** Even with `unasync`, they use `sed`
   passes to clean up things the library doesn't handle:
   - Removing bare `import asyncio` lines
   - Rewriting `asyncio.run(main())` → `main()` in examples
   - Swapping pytest markers (`pytest.mark.asyncio` → `pytest.mark.sync`)

3. **Code formatting runs after generation.** They run `black` + `isort` on the
   generated output to normalize formatting, since token replacement can produce
   style that doesn't match the project. We use `ruff format` + `ruff check
   --fix` for the same purpose.

4. **Drift detection uses a temp directory, not `git diff`.** The `--check` flag
   generates to a `_sync_check/` temp directory and runs `diff` against the
   committed `_sync/`. This is more robust than `git diff` because it works
   regardless of git state and catches problems even if `_sync/` was never
   committed.

5. **No "DO NOT EDIT" headers.** They rely on the `_sync/` directory convention
   alone. The directory name is sufficient signal.

6. **Tests are generated too.** Async DSL tests in `test_elasticsearch/test_dsl/_async/`
   are transformed to sync tests in `test_elasticsearch/test_dsl/_sync/`. Test-specific
   replacements include `assert_awaited_once_with` → `assert_called_once_with`
   and `asynccontextmanager` → `contextmanager`.

7. **Task runner integration.** They use `nox`: `nox -rs format` runs generation +
   formatting, `nox -rs lint` runs `--check` mode. We wire this into our existing
   `uv run` workflow instead.

## Target Public API

```python
# Sync
from spotify_sdk import SpotifyClient

with SpotifyClient(access_token="...") as client:
    album = client.albums.get("4aawyAB9vmqN3uQ7FjRGTy")

# Async
from spotify_sdk import AsyncSpotifyClient

async with AsyncSpotifyClient(access_token="...") as client:
    album = await client.albums.get("4aawyAB9vmqN3uQ7FjRGTy")
```

The `_async` method suffix goes away entirely. Each client class has a single,
unambiguous set of methods.

## Directory Structure

```
src/spotify_sdk/
├── __init__.py                  # Exports AsyncSpotifyClient, SpotifyClient, exceptions
├── _async/                      # SOURCE OF TRUTH (hand-written)
│   ├── __init__.py
│   ├── _base_client.py          # AsyncBaseClient
│   ├── _base_service.py         # AsyncBaseService
│   ├── _client.py               # AsyncSpotifyClient
│   └── services/
│       ├── __init__.py
│       ├── albums.py            # AsyncAlbumService
│       └── tracks.py            # AsyncTrackService
├── _sync/                       # AUTO-GENERATED (do not hand-edit)
│   ├── __init__.py
│   ├── _base_client.py          # BaseClient
│   ├── _base_service.py         # BaseService
│   ├── _client.py               # SpotifyClient
│   └── services/
│       ├── __init__.py
│       ├── albums.py            # AlbumService
│       └── tracks.py            # TrackService
├── exceptions.py                # Shared (no I/O, never duplicated)
└── models/                      # Shared (no I/O, never duplicated)
    ├── __init__.py
    ├── base.py
    ├── common.py
    ├── album.py
    ├── artist.py
    └── track.py
```

Models and exceptions contain no I/O. They are shared directly by both client
variants and are never duplicated or generated.

## Test Structure

```
tests/
├── _async/                      # Source of truth (hand-written)
│   ├── test_base_client.py
│   ├── test_album_service.py
│   ├── test_track_service.py
│   └── test_client.py
├── _sync/                       # Auto-generated (do not hand-edit)
│   ├── test_base_client.py
│   ├── test_album_service.py
│   ├── test_track_service.py
│   └── test_client.py
├── test_exceptions.py           # Shared (no I/O, tested directly)
├── conftest.py
└── fixtures/
    └── ...
```

## The Unasync Script

`scripts/run_unasync.py` — a thin wrapper around the
[`unasync`](https://github.com/python-trio/unasync) library. The `unasync`
library handles all standard async-to-sync transformations (`async def` → `def`,
`await` removal, `async with` → `with`, etc.) automatically. We configure
project-specific class name replacements via `additional_replacements` and apply
light post-processing for things the library doesn't cover.

### How It Works

The script defines `unasync.Rule` objects that map source directories to output
directories, with a replacements dict for project-specific tokens:

```python
import unasync

rule = unasync.Rule(
    fromdir="src/spotify_sdk/_async/",
    todir="src/spotify_sdk/_sync/",
    additional_replacements={
        "AsyncSpotifyClient": "SpotifyClient",
        "AsyncBaseClient": "BaseClient",
        "AsyncBaseService": "BaseService",
        "AsyncAlbumService": "AlbumService",
        "AsyncTrackService": "TrackService",
        # Override unasync default Async→Sync prefix to get httpx.Client
        # (not httpx.SyncClient).
        "AsyncClient": "Client",
        "aclose": "close",
        "_async": "_sync",
    },
)
```

The `unasync` library handles these transformations automatically (no config
needed):

| Async (source of truth)     | Sync (generated)            |
|-----------------------------|-----------------------------|
| `async def`                 | `def`                       |
| `await expr`                | `expr`                      |
| `async with`                | `with`                      |
| `async for`                 | `for`                       |
| `__aenter__`                | `__enter__`                 |
| `__aexit__`                 | `__exit__`                  |
| `__aiter__`                 | `__iter__`                  |
| `__anext__`                 | `__next__`                  |

These are configured via `additional_replacements`:

| Async (source of truth)     | Sync (generated)            |
|-----------------------------|-----------------------------|
| `AsyncSpotifyClient`        | `SpotifyClient`             |
| `AsyncBaseClient`           | `BaseClient`                |
| `AsyncBaseService`          | `BaseService`               |
| `AsyncAlbumService`         | `AlbumService`              |
| `AsyncTrackService`         | `TrackService`              |
| `AsyncClient` (httpx)       | `Client`                    |
| `aclose`                    | `close`                     |
| `_async` (import paths)     | `_sync`                     |

These are handled by post-processing (Python regex replacement) after `unasync`
runs:

| Pattern                     | Replacement                 |
|-----------------------------|-----------------------------|
| `import anyio`              | *(removed)*                 |
| `anyio.sleep`               | `time.sleep`                |
| `@pytest.mark.anyio`        | *(removed)*                 |
| `@patch("anyio.sleep")`     | `@patch("time.sleep")`      |

After all transformations, the script runs `ruff format` and `ruff check --fix`
on the output to normalize formatting.

### Test Transformations

The script processes tests using a second rule with the same
`additional_replacements` dict, plus test-specific entries:

```python
test_rule = unasync.Rule(
    fromdir="tests/_async/",
    todir="tests/_sync/",
    additional_replacements={
        **source_replacements,
        "assert_awaited_once_with": "assert_called_once_with",
    },
)
```

### Invocation

```
# Generate sync code from async source
python scripts/run_unasync.py

# Check for drift (CI mode — fails if _sync/ is out of date)
python scripts/run_unasync.py --check
```

The `--check` flag generates to a temporary `_sync_check/` directory, diffs it
against the committed `_sync/`, and exits non-zero if there are differences.
This is the same approach used by elasticsearch-py.

## When Unasync Runs

### During Development

1. Developer edits files in `_async/` only.
2. Developer runs `python scripts/run_unasync.py`.
3. Both `_async/` and `_sync/` are committed together.

### In CI (Drift Detection)

A job in `.github/workflows/ci.yml` runs the script in `--check` mode. This
generates sync code to a temp `_sync_check/` directory and diffs it against the
committed `_sync/`. If there's any difference, the job fails.

This catches two problems: hand-edits to `_sync/` and forgotten regeneration
after `_async/` changes.

```yaml
sync-check:
  runs-on: ubuntu-latest
  name: Sync Check
  steps:
    - uses: actions/checkout@...
      with:
        persist-credentials: false
    - uses: astral-sh/setup-uv@...
      with:
        python-version-file: .python-version
    - name: Install dependencies
      run: uv sync --group codegen
    - name: Check sync code is up to date
      run: uv run python scripts/run_unasync.py --check
```

### At Release

No changes to the release pipeline. `uv build` packages whatever is committed.
Since generated code is already in the tree, the existing `release.yml` workflow
works as-is.

## Breaking Changes

This is a breaking change for async users:

| Before                                           | After                                            |
|--------------------------------------------------|--------------------------------------------------|
| `from spotify_sdk import SpotifyClient`          | `from spotify_sdk import AsyncSpotifyClient`     |
| `await client.albums.get_async("123")`           | `await client.albums.get("123")`                 |
| `await client.albums.get_several_async([...])`   | `await client.albums.get_several([...])`         |
| `await client.albums.get_tracks_async("123")`    | `await client.albums.get_tracks("123")`          |
| `await client.aclose()`                          | `await client.close()`                           |

Sync users are unaffected — their imports and method calls remain the same.

This warrants a version bump to **0.2.0**.

## Alternatives Considered

### Keep the unified class, use runtime dispatch

A single class that detects whether it's in an async context and dispatches
accordingly. Rejected: implicit runtime behavior is fragile, hard to type-check,
and makes the API confusing (is `get()` sync or async?).

### Write a custom tokenize-based script instead of using `unasync`

Build our own async-to-sync transformer using Python's `tokenize` module. This
was the original proposal, under the assumption that the `unasync` library was
unmaintained. After reviewing elasticsearch-py — which depends on `unasync>=0.6.0`
and has used it successfully at scale for years — this assumption was revised. The
library is stable (feature-complete, not abandoned), and its
`additional_replacements` mechanism covers all our project-specific needs. A
custom script would reimplement what `unasync` already does, with more surface
area for bugs.

### Generate at build time (not committed)

Generate `_sync/` during `uv build` and add it to `.gitignore`. Rejected: IDEs
can't see the sync code, `pyright` can't type-check it locally, and developers
can't grep or review it. Committing generated code with CI drift detection is the
approach taken by `httpcore`, `httpx`, and `elasticsearch-py` for the same
reasons.

### Use `anyio` as the async backend

Write code against `anyio` instead of `asyncio` directly, getting Trio support
for free. This was adopted as part of this implementation — the async code uses
`anyio.sleep` for backoff delays, and the unasync post-processing converts these
to `time.sleep` in the sync variant.

## Appendix: Implementation Steps

These were the steps followed during the original implementation:

1. **Write the Unasync Script** — Add `unasync>=0.6.0` to a `codegen` dependency
   group. Create `scripts/run_unasync.py` with `unasync.Rule` configuration and
   post-processing.

2. **Restructure Source into `_async/`** — Move and refactor current source files.
   Remove sync-only code, rename `request_async` to `request`, etc.

3. **Generate `_sync/`** — Run `scripts/run_unasync.py`. Verify the generated sync
   code is functionally equivalent to the old hand-written sync code.

4. **Update `__init__.py`** — Export both `AsyncSpotifyClient` and `SpotifyClient`.

5. **Restructure Tests** — Move async tests into `tests/_async/`. Run the unasync
   script to generate `tests/_sync/`.

6. **Add CI Sync-Check Job** — Add drift detection to `.github/workflows/ci.yml`.

7. **Clean Up** — Delete the original top-level files now replaced by `_async/`
   and `_sync/`.

8. **Update Dependencies** — Add `unasync` to the `codegen` group; add `anyio` to
   the test dependencies:

   ```toml
   [dependency-groups]
   test = [
       "anyio[trio]>=4.12.1",
       "pytest>=9.0.2",
       "pytest-httpx>=0.36.0",
   ]
   codegen = [
     {include-group = "lint"},
     "unasync>=0.6.0",
   ]
   dev = [
     {include-group = "lint"},
     {include-group = "test"},
     {include-group = "typecheck"},
     {include-group = "codegen"},
     "jmeslog>=0.2.0",
   ]
   ```
