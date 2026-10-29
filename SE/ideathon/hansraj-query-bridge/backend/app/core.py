"""Shared primitives for the use-case procedures.

The pseudocode returns three shapes -- `return error "..."`, `return success "...", data`
and `return response "...", action "...", reason "..."`. `Result` models all three so the
procedures stay line-for-line comparable with the documents, and the API layer can map
them to HTTP status codes in one place."""
from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional


class DatabaseException(Exception):
    pass


class NetworkException(Exception):
    pass


class SystemException(Exception):
    pass


@dataclass
class Result:
    kind: str                     # "error" | "success" | "response"
    message: str
    data: Any = None
    action: Optional[str] = None
    reason: Optional[str] = None
    extra: dict = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.kind == "error"

    @property
    def is_success(self) -> bool:
        return self.kind == "success"

    @property
    def http_status(self) -> int:
        if self.kind != "error":
            return 200
        m = self.message
        if m.startswith("Validation Failed"):
            return 400
        if m.startswith("Authentication Failed"):
            return 401
        if m.startswith("Security Error"):
            return 403
        if m.startswith(("State Error", "Concurrency Error")):
            return 409
        if m.startswith(("Database Error: User verified externally", "Database Error: User lacks")):
            return 403
        if m.startswith("Database Error") and (
                "not found" in m or m.startswith(("Database Error: Invalid", "Database Error: Target"))):
            return 404
        if "unavailable" in m or m.startswith("Cloud Error"):
            return 503
        return 500

    def as_dict(self) -> dict:
        d = {"kind": self.kind, "message": self.message}
        if self.data is not None:
            d["data"] = self.data
        if self.action:
            d["action"] = self.action
        if self.reason:
            d["reason"] = self.reason
        d.update(self.extra)
        return d


def err(message: str) -> Result:
    return Result("error", message)


def success(message: str, data: Any = None, **extra) -> Result:
    return Result("success", message, data, extra=extra)


def response(message: str, action: str, reason: Optional[str] = None, **extra) -> Result:
    return Result("response", message, action=action, reason=reason, extra=extra)


# ---- typeof() helpers (pseudocode: typeof(x) != "string") --------------------------------
def is_str(x) -> bool:
    return isinstance(x, str)


def is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def is_float(x) -> bool:
    return isinstance(x, float)


def is_bool(x) -> bool:
    return isinstance(x, bool)


def is_dict(x) -> bool:
    return isinstance(x, dict)


def first(rows):
    """Pseudocode treats single-row lookups as `record is empty` checks."""
    if not rows:
        return None
    return rows[0] if isinstance(rows, list) else rows


def cosine_similarity(a, b) -> Optional[float]:
    """Explicit cosine math from UC-02 step 4 (no "magic" functions). Returns None when a
    zero-magnitude vector makes the similarity undefined (division-by-zero guard)."""
    dot = 0.0
    mag_q = 0.0
    mag_e = 0.0
    for i in range(len(a)):
        dot += a[i] * b[i]
        mag_q += a[i] * a[i]
        mag_e += b[i] * b[i]
    mag_q = math.sqrt(mag_q)
    mag_e = math.sqrt(mag_e)
    if mag_q > 0 and mag_e > 0:
        return dot / (mag_q * mag_e)
    return None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


ROLE_SQL = ("SELECT R.role_name FROM USERS U JOIN ROLE R ON U.role_id = R.role_id "
            "WHERE U.user_id = ?")


@dataclass
class Gateways:
    """External-service adapters. Replaceable in tests and at deploy time."""
    auth: Any = None          # .call(username, password) -> obj(status_code, user_identity)
    embedder: Any = None      # .generate_embedding(text, task) -> list[float]
    llm: Any = None           # .generate_grounded_response(query, context) -> str
    storage: Any = None       # .upload_stream(stream, name, query_id) -> key ; .delete(key)
    timetable: Any = None     # .fetch(tic_id, date) -> list[{start_time,end_time}]
    email: Any = None         # .send(to, subject, body) -> obj(status_code)
    jwt: Any = None           # .generate(user_id, role_name, ttl) -> token


def _noop(*_a, **_k):
    return None


@dataclass
class Ctx:
    db: Any
    gw: Gateways
    log_error: Callable = _noop
    dispatch: Callable = _noop                   # DispatchNotificationAsync (fire & forget)
    now: Callable = now_iso
    new_id: Callable = new_id
    vector_search: Optional[Callable] = None     # pgvector top-K (production path of UC-02)
    kb_manage: Optional[Callable] = None         # KnowledgeBaseManagement hook (UC-09/13)


def sanitize_text(text: str) -> str:
    """Strip control characters (keeps newlines/tabs) from stored free text."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
