"""Composition of readiness checks; imports never connect to external services."""

from app.core.settings import get_settings
from app.infrastructure.readiness import mysql_is_ready, qdrant_is_ready


def check_mysql() -> bool:
    return mysql_is_ready(get_settings())


def check_qdrant() -> bool:
    return qdrant_is_ready(get_settings())
