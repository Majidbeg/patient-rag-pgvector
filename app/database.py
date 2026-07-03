"""
Single place for Postgres connections. Uses a simple connection pool
so FastAPI request handlers don't open/close a raw connection every call.
"""
import psycopg2
from psycopg2 import pool
from app.config import settings

_connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)


def get_connection():
    return _connection_pool.getconn()


def release_connection(conn):
    _connection_pool.putconn(conn)
