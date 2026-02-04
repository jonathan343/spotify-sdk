"""Fail if sync modules export classes with a Sync* prefix."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys


def iter_sync_modules() -> list[str]:
    """Return all module names under spotify_sdk._sync."""
    package = importlib.import_module("spotify_sdk._sync")
    prefix = f"{package.__name__}."
    module_names = []
    for module_info in pkgutil.walk_packages(package.__path__, prefix):
        module_names.append(module_info.name)
    return module_names


def main() -> int:
    """Return a non-zero exit code if any Sync-prefixed classes exist."""
    violations: list[str] = []
    for module_name in iter_sync_modules():
        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            if obj.__name__.startswith("Sync"):
                violations.append(f"{module.__name__}.{obj.__name__}")

    if violations:
        for violation in sorted(violations):
            print(f"Sync-prefixed class found: {violation}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
