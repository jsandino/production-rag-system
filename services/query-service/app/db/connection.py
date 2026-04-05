import psycopg
from psycopg import Connection

from app.core.settings import get_settings


def get_connection() -> Connection:
    """
    Create a new PostgreSQL connection.
    Caller is responsible for closing it.
    """
    return psycopg.connect(get_settings().database_url)
