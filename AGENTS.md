# Repository Guidelines

## Project Structure & Module Organization
- `src/spotify_sdk/_async/`: Canonical async-first implementation. Edit here first.
- `src/spotify_sdk/_sync/`: Auto-generated sync API (do not edit directly).
- `src/spotify_sdk/models/`: Pydantic models for Spotify API responses.
- `tests/_async/` and `tests/_sync/`: Tests mirror the async/sync split; sync tests are generated from async.
- `docs/`: User documentation sources; `site/` holds the built site output.
- `scripts/`: Developer utilities such as `run_unasync.py`.

## Build, Test, and Development Commands
```bash
uv sync                             # Install deps
uv run pytest                       # Run all tests
uv run ruff check .                 # Lint
uv run ruff format --check --preview .  # Formatting check
uv run pyright                      # Type checking
uv run python scripts/run_unasync.py    # Regenerate sync code
uv run python scripts/run_unasync.py --check  # Verify sync is current
uv run zensical build --clean       # Build docs site
```

## Coding Style & Naming Conventions
- Python 3.10+, full type hints, line length 79.
- Google-style docstrings enforced via Ruff.
- Keep private attributes prefixed with `_`.
- For reserved keywords, use `type_` with `Field(alias="type")`.
- Prefer updating `_async` code and regenerating `_sync` via `unasync`.
- When adding any `Async*` classes, update `scripts/run_unasync.py` to map
  `AsyncX` to `X` so sync code does not keep the `Async` prefix.
- When adding new docs pages, update `zensical.toml` nav so the page appears
  in the built site.
- Use clearly fake placeholder IDs in docs examples to avoid implying they are
  real, valid Spotify IDs.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-httpx`, `anyio`.
- Async tests use `@pytest.mark.anyio`.
- Test class names are descriptive (e.g., `TestAlbumServiceGet`).
- Run `uv run pytest` after regenerating sync code to cover both variants.

## Commit & Pull Request Guidelines
- Commit subjects are short, imperative sentences like `Add PlaylistService...`, `Fix docs build...`, or `Bump ruff...`.
- Release commits follow `Release: vX.Y.Z (#NN)`.
- PRs should include: a clear summary, tests run, and note if `run_unasync.py` was executed.
- Include docs updates when public APIs or behavior change.

## Agent Workflow & Safety
- Never edit `src/spotify_sdk/_sync/` or `tests/_sync/` directly; regenerate from `_async`.
- Use `uv run` for tools and tests to match CI behavior.
- Ask before destructive or external actions (publishing, emailing, `rm -rf`, etc.).
- Keep changes scoped and explain any generated updates in the PR.

## Session Checklist
- Skim `README.md` for context and `docs/` when touching public behavior.
- If you changed `_async/` or `tests/_async/`, run `scripts/run_unasync.py` before tests.
- Prefer updating docs alongside any public API or behavior change.
