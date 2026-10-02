"""Dependency errors shared across business modules and adapters."""


class DependencyTimeout(RuntimeError):
    """An external dependency exceeded its configured timeout."""
