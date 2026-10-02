"""Dependency errors shared across business modules and adapters."""


class DependencyTimeout(RuntimeError):
    """An external dependency exceeded its configured timeout."""


class DependencyUnavailable(RuntimeError):
    """An external dependency failed before returning a usable response."""
