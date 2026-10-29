"""Test harness: a scriptable fake database and context factory so each use-case procedure can
be driven down every branch (including DatabaseException / NetworkException paths) without
infrastructure. Real-PostgreSQL behaviour is covered by test_api_integration.py."""
from types import SimpleNamespace as NS

from app.core import Ctx, DatabaseException, Gateways, NetworkException  # noqa: F401

DB_ERR = DatabaseException("simulated database failure")
NET_ERR = NetworkException("simulated network failure")


class Seq:
    """Return successive values on successive matching calls (last value repeats)."""
    def __init__(self, *values):
        self.values, self.i = list(values), 0

    def next(self):
        v = self.values[min(self.i, len(self.values) - 1)]
        self.i += 1
        return v


class FakeDb:
    def __init__(self):
        self.routes, self.calls, self.events = [], [], []

    def on(self, fragment, value):
        self.routes.append((fragment, value))
        return self

    def _go(self, kind, sql, params):
        self.calls.append((kind, sql, list(params)))
        for fragment, val in self.routes:
            if fragment in sql:
                if isinstance(val, Seq):
                    val = val.next()
                if callable(val):
                    val = val(list(params))
                if isinstance(val, Exception):
                    raise val
                return val
        return [] if kind == "query" else 1

    def query(self, sql, params=()):
        return self._go("query", sql, params)

    def insert(self, sql, params=()):
        return self._go("insert", sql, params)

    def update(self, sql, params=()):
        return self._go("update", sql, params)

    def begin(self):
        self.events.append("begin")

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")

    def n(self, fragment):
        return sum(1 for _, sql, _ in self.calls if fragment in sql)


def role(name):
    return [{"role_name": name}]


def make_ctx(db=None, dispatch_raises=False, **gw):
    logs, sent = [], []

    def dispatch(*args):
        sent.append(args)
        if dispatch_raises:
            raise NetworkException("notification service down")

    ctx = Ctx(db=db or FakeDb(), gw=Gateways(**gw), log_error=lambda e: logs.append(str(e)),
              dispatch=dispatch, now=lambda: "2026-10-29T10:00:00+00:00", new_id=lambda: "NEW-ID")
    ctx.logs, ctx.sent = logs, sent
    return ctx


def msg(result):
    return result.message
