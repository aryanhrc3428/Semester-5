"""PostgreSQL access. Exposes the pseudocode's database vocabulary:
executeParameterizedQuery / Insert / Update, beginTransaction, commitTransaction,
rollbackTransaction. Every statement is parameterized (`?` placeholders) -- no string
concatenation of user input ever reaches SQL (SRS 3.6.7)."""
from __future__ import annotations

import datetime as _dt
import decimal
import json
import os
import uuid
from contextlib import contextmanager
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .core import DatabaseException

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def _to_sql(sql: str) -> str:
    return sql.replace("%", "%%").replace("?", "%s")


def _param(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and v and all(isinstance(x, (int, float)) for x in v):
        return "[" + ",".join(repr(float(x)) for x in v) + "]"      # pgvector literal
    if isinstance(v, dict):
        return json.dumps(v)
    return v


def _value(key: str, v: Any) -> Any:
    if isinstance(v, _dt.datetime):
        return v.isoformat()
    if isinstance(v, _dt.date):
        return v.isoformat()
    if isinstance(v, _dt.time):
        return v.strftime("%H:%M")
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, uuid.UUID):
        return str(v)
    if key == "embedding" and isinstance(v, str) and v.startswith("["):
        return json.loads(v)
    return v


class Db:
    """Thin wrapper over one psycopg connection (autocommit; explicit BEGIN/COMMIT)."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def query(self, sql: str, params: Iterable = ()) -> list[dict]:
        try:
            cur = self.conn.execute(_to_sql(sql), [_param(p) for p in params])
            rows = cur.fetchall() if cur.description else []
        except psycopg.Error as exc:
            raise DatabaseException(str(exc)) from exc
        return [{k: _value(k, v) for k, v in r.items()} for r in rows]

    def insert(self, sql: str, params: Iterable = ()) -> int:
        return self.update(sql, params)

    def update(self, sql: str, params: Iterable = ()) -> int:
        try:
            cur = self.conn.execute(_to_sql(sql), [_param(p) for p in params])
            return cur.rowcount
        except psycopg.Error as exc:
            raise DatabaseException(str(exc)) from exc

    def begin(self) -> None:
        try:
            self.conn.execute("BEGIN")
        except psycopg.Error as exc:
            raise DatabaseException(str(exc)) from exc

    def commit(self) -> None:
        try:
            self.conn.execute("COMMIT")
        except psycopg.Error as exc:
            raise DatabaseException(str(exc)) from exc

    def rollback(self) -> None:
        try:
            self.conn.execute("ROLLBACK")
        except psycopg.Error:
            pass


class Database:
    """Connection pool + schema bootstrap."""

    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 20):
        self.dsn = dsn
        self.pool = ConnectionPool(
            dsn, min_size=min_size, max_size=max_size, open=False,
            kwargs={"autocommit": True, "row_factory": dict_row},
        )

    def open(self) -> None:
        self.pool.open(wait=True, timeout=15)

    def close(self) -> None:
        self.pool.close()

    @contextmanager
    def session(self):
        with self.pool.connection() as conn:
            yield Db(conn)

    def healthy(self) -> bool:
        try:
            with self.session() as db:
                db.query("SELECT 1 AS ok")
            return True
        except Exception:
            return False


def ensure_database(dsn: str) -> None:
    """Create the target database when it does not exist (local convenience)."""
    info = psycopg.conninfo.conninfo_to_dict(dsn)
    name = info.get("dbname") or "hansraj_qb"
    admin = dict(info, dbname="postgres")
    with psycopg.connect(**admin, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", [name]).fetchone()
        if not exists:
            conn.execute(f'CREATE DATABASE "{name}"')


def apply_schema(dsn: str) -> None:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        ddl = fh.read()
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(ddl)
