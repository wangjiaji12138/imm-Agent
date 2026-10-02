"""Readiness checks for required local services."""

import httpx
import pymysql

from app.core.settings import Settings


def mysql_is_ready(settings: Settings) -> bool:
    """Return whether MySQL accepts a short authenticated connection."""

    try:
        connection = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            connect_timeout=2,
            read_timeout=2,
            write_timeout=2,
        )
    except pymysql.MySQLError:
        return False

    connection.close()
    return True


def qdrant_is_ready(settings: Settings) -> bool:
    """Return whether Qdrant reports that it is ready for traffic."""

    try:
        response = httpx.get(f"{settings.qdrant_url.rstrip('/')}/readyz", timeout=2.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False
