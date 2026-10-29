"""Hansraj Query Bridge API (FastAPI). Every route is a thin wrapper that authenticates the caller
from the JWT, takes the acting user's id from the token (never from the request body, preventing
IDOR), calls the matching use-case procedure and maps its Result to HTTP."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field, StrictBool

from .config import settings
from .core import DatabaseException, NetworkException, Result, new_id
from .db import Database
from .gateways import build_gateways
from .runtime import build_ctx, make_dispatcher
from .security import LoginLockout, RateLimiter, keyword_department, looks_malicious
from .usecases.admin import (KB_ROLE_SQL, admin_resolve_query, admin_view_new_queries, forward_query_to_tic,
                             knowledge_base_management)
from .usecases.auth import authenticate
from .usecases.rag import resolve_query_rag
from .usecases.student import (load_student_dashboard, raise_new_query, upload_document,
                               view_request_slot_and_accept_meeting)
from .usecases.tic import (manage_meeting, tic_request_document, tic_resolve_query, tic_review_document,
                           tic_view_assigned_queries, view_timetable_availability)

log = logging.getLogger("hqb.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


class State:
    database: Database
    gw = None
    dispatch = None
    ai_limiter: RateLimiter
    lockout: LoginLockout


S = State()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("AUTO_SETUP", "true").lower() in ("1", "true", "yes"):
        from .seed import seed
        seed()
    S.database = Database(settings.database_url)
    S.database.open()
    S.gw = build_gateways(settings, S.database)
    S.dispatch = make_dispatcher(S.database, S.gw)
    S.ai_limiter = RateLimiter(settings.ai_rate_per_minute, 60)
    S.lockout = LoginLockout(settings.lockout_attempts, settings.lockout_seconds)
    log.info("AI mode: %s | email: %s | storage: %s | RAG threshold: %.2f",
             "Gemini" if settings.uses_gemini else "local fallback",
             "Resend" if settings.resend_api_key else "log only", settings.storage_backend,
             settings.similarity_threshold)
    yield
    S.database.close()


app = FastAPI(title="Hansraj Query Bridge API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


# ------------------------------------------------------------------------------ dependencies
def get_ctx():
    with S.database.session() as db:
        yield build_ctx(db, S.gw, S.dispatch)


def fail(result: Result):
    raise HTTPException(result.http_status, result.message)


def ok(result: Result):
    if result.is_error:
        fail(result)
    return result.as_dict()


def audit(ctx, user_id, action, entity, entity_id=None, details=None):
    try:
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, details, timestamp) "
                      "VALUES (?, ?, ?, ?, ?, ?)", [user_id, action, entity, entity_id, details, ctx.now()])
    except DatabaseException as exc:
        log.warning("audit write failed: %s", exc)


def current_user(request: Request, ctx=Depends(get_ctx)) -> dict:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    try:
        claims = S.gw.jwt.decode(header[7:])
    except Exception:
        raise HTTPException(401, "Session expired or invalid. Please sign in again.")
    sess = ctx.db.query("SELECT revoked FROM SESSIONS WHERE jti = ?", [claims.get("jti")])
    if not sess or sess[0]["revoked"]:
        raise HTTPException(401, "Session expired or invalid. Please sign in again.")
    rows = ctx.db.query(
        "SELECT U.user_id, U.name, U.email, U.department_id, U.kb_permission, U.is_active, R.role_name "
        "FROM USERS U JOIN ROLE R ON U.role_id = R.role_id WHERE U.user_id = ?", [claims["sub"]])
    if not rows or not rows[0]["is_active"]:
        raise HTTPException(401, "Account is not active")
    u = rows[0]
    u["jti"] = claims["jti"]
    return u


def require(*roles):
    def dep(user=Depends(current_user)):
        if user["role_name"] not in roles:
            raise HTTPException(403, "Security Error: You do not have access to this resource")
        return user
    return dep


student_only, admin_only, tic_only = require("Student"), require("Admin"), require("TIC")
any_user = require("Student", "Admin", "TIC")
kb_user = require("Admin", "TIC")


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


# ------------------------------------------------------------------------------ models
class LoginBody(BaseModel):
    username: str
    password: str


class AskBody(BaseModel):
    query: str


class RaiseBody(BaseModel):
    title: Optional[str] = Field(default=None, max_length=150)
    description: str
    department_id: str
    category: str
    from_ai: bool = False


class ResolveBody(BaseModel):
    resolution: str
    add_to_kb: StrictBool = False


class ForwardBody(BaseModel):
    tic_id: str


class DocRequestBody(BaseModel):
    note: str


class ReviewBody(BaseModel):
    decision: str
    notes: Optional[str] = None


class SlotRequestBody(BaseModel):
    slot_id: str
    query_id: str


class SlotCreateBody(BaseModel):
    date: str
    start_time: str
    end_time: str


class MeetingBody(BaseModel):
    query_id: str
    date: str
    start_time: str
    end_time: str


class KbBody(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    source: Optional[str] = None


class KbUpdateBody(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None


# ------------------------------------------------------------------------------ auth (UC-01)
@app.get("/api/health")
def health():
    return {"status": "ok", "database": S.database.healthy(), "ai": "gemini" if settings.uses_gemini else "local",
            "email": "resend" if settings.resend_api_key else "log"}


@app.post("/api/auth/login")
def login(body: LoginBody, request: Request, ctx=Depends(get_ctx)):
    key = f"{client_ip(request)}|{body.username.lower()}"
    wait = S.lockout.locked_for(key)
    if wait:
        raise HTTPException(429, f"Too many failed attempts. Try again in {wait // 60 + 1} minute(s).")
    result = authenticate(ctx, body.username, body.password)
    if result.is_error:
        if result.message.startswith("Authentication Failed"):
            S.lockout.record_failure(key)
        audit(ctx, "anonymous", "Login Failed", "Session", None, result.message)
        fail(result)
    S.lockout.reset(key)
    data = result.data
    claims = S.gw.jwt.decode(data["session_token"])
    ctx.db.insert("INSERT INTO SESSIONS (jti, user_id, expires_at) VALUES (?, ?, to_timestamp(?))",
                  [claims["jti"], data["user_id"], claims["exp"]])
    ctx.db.update("UPDATE USERS SET last_login_at = now() WHERE user_id = ?", [data["user_id"]])
    audit(ctx, data["user_id"], "Login", "Session", claims["jti"])
    u = ctx.db.query("SELECT name, email, department_id FROM USERS WHERE user_id = ?", [data["user_id"]])[0]
    return {"token": data["session_token"], "dashboard_url": data["dashboard_url"],
            "user": {"user_id": data["user_id"], "role": data["role_name"], **u}}


@app.post("/api/auth/logout")
def logout(user=Depends(any_user), ctx=Depends(get_ctx)):
    ctx.db.update("UPDATE SESSIONS SET revoked = TRUE WHERE jti = ?", [user["jti"]])
    audit(ctx, user["user_id"], "Logout", "Session", user["jti"])
    return {"message": "Signed out"}


@app.get("/api/me")
def me(user=Depends(any_user)):
    return {"user_id": user["user_id"], "name": user["name"], "email": user["email"], "role": user["role_name"],
            "department_id": user["department_id"], "kb_permission": user["kb_permission"]}


@app.get("/api/departments")
def departments(user=Depends(any_user), ctx=Depends(get_ctx)):
    return ctx.db.query("SELECT dept_id, department_name, department_code FROM DEPARTMENTS ORDER BY department_name")


# ------------------------------------------------------------------------------ helpers
def load_query(ctx, user, query_id: str) -> dict:
    rows = ctx.db.query(
        "SELECT Q.*, S.name AS student_name, S.email AS student_email, T.name AS tic_name, D.department_name "
        "FROM D3_QUERIES Q JOIN USERS S ON S.user_id = Q.student_id LEFT JOIN USERS T ON T.user_id = Q.assigned_tic "
        "LEFT JOIN DEPARTMENTS D ON D.dept_id = Q.department_id WHERE Q.query_id = ?", [query_id])
    if not rows:
        raise HTTPException(404, "Database Error: Target query reference not found")
    q = rows[0]
    role = user["role_name"]
    if (role == "Student" and q["student_id"] != user["user_id"]) or \
            (role == "TIC" and q["assigned_tic"] != user["user_id"]):
        raise HTTPException(403, "Security Error: You do not have access to this query")
    return q


def suggest_department(ctx, text: str) -> Optional[str]:
    depts = ctx.db.query("SELECT dept_id, department_name, department_code FROM DEPARTMENTS")
    try:
        found = ctx.gw.llm.classify_department(text, depts)
    except NetworkException:
        found = None
    return found or keyword_department(text, {d["department_code"]: d["dept_id"] for d in depts})


# ------------------------------------------------------------------------------ student: AI (UC-02)
@app.post("/api/student/ask")
def ask_ai(body: AskBody, user=Depends(student_only), ctx=Depends(get_ctx)):
    text = body.query.strip()
    if not S.ai_limiter.allow(user["user_id"]):
        raise HTTPException(429, "You are sending questions too quickly. Please wait a moment.")
    if len(text) < 5 or len(text) > 1000:
        raise HTTPException(400, "Validation Failed: Query length out of bounds")
    if looks_malicious(text):
        audit(ctx, user["user_id"], "Blocked Malicious Input", "AI Query", None, text[:200])
        raise HTTPException(400, "This message can't be processed. Please rephrase your question.")
    if len(text.split()) < 3:
        return {"status": "clarify", "message": "Could you add a little more detail? For example, what exactly "
                                                "do you need and for which course or semester?"}
    result = resolve_query_rag(ctx, text, float(settings.similarity_threshold))
    sources, answer, conf, status, reason = [], None, None, "escalate", None
    if result.is_error:
        ctx.db.insert("INSERT INTO AI_INTERACTIONS (interaction_id, student_id, query_text, response_status) "
                      "VALUES (?, ?, ?, ?)", [new_id(), user["user_id"], text, "Error"])
        raise HTTPException(result.http_status, result.message)
    if result.kind == "success":
        d = result.data
        answer, conf = d["answer"].strip(), d["confidence"]
        if answer.upper().startswith("INSUFFICIENT_CONTEXT"):
            reason = "The verified knowledge base does not fully answer this."
        else:
            status = "answered"
            for k in d["kb_ids"][:3]:
                found = ctx.db.query("SELECT kb_id, title, source FROM D2_KNOWLEDGE WHERE kb_id = ?", [k])
                if found:
                    sources.append(found[0])
    else:
        reason = result.reason
    ctx.db.insert("INSERT INTO AI_INTERACTIONS (interaction_id, student_id, query_text, response_status, "
                  "answer_text, source_ids, confidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  [new_id(), user["user_id"], text, status, answer if status == "answered" else None,
                   ",".join(s["kb_id"] for s in sources), conf])
    out = {"status": status, "confidence": conf, "sources": sources}
    if status == "answered":
        out["answer"] = answer
    else:
        out["message"] = ("I couldn't find a verified answer for this. You can send it to the college staff "
                          "and they will reply here.")
        out["reason"] = reason
        out["suggested_department_id"] = suggest_department(ctx, text)
    return out


@app.post("/api/student/suggest-department")
def suggest_dept(body: AskBody, user=Depends(student_only), ctx=Depends(get_ctx)):
    return {"department_id": suggest_department(ctx, body.query)}


# ------------------------------------------------------------------------------ student: queries (UC-03/04)
@app.post("/api/student/queries")
def raise_query(body: RaiseBody, user=Depends(student_only), ctx=Depends(get_ctx)):
    text = body.description.strip()
    if looks_malicious(text):
        audit(ctx, user["user_id"], "Blocked Malicious Input", "Query", None, text[:200])
        raise HTTPException(400, "This message can't be processed. Please rephrase your query.")
    if body.title and body.title.strip():
        text = f"{body.title.strip()}: {text}"
    result = raise_new_query(ctx, user["user_id"], text, body.department_id, body.category)
    data = ok(result)
    ctx.db.update("UPDATE D3_QUERIES SET source = ? WHERE query_id = ?",
                  ["AI Escalation" if body.from_ai else "Direct Raise", result.data["query_id"]])
    return data


@app.get("/api/student/queries")
def my_queries(user=Depends(student_only), ctx=Depends(get_ctx)):
    return ok(load_student_dashboard(ctx, user["user_id"]))


@app.get("/api/queries/{query_id}")
def query_detail(query_id: str, user=Depends(any_user), ctx=Depends(get_ctx)):
    q = load_query(ctx, user, query_id)
    docs = ctx.db.query("SELECT document_id, file_name, file_type, file_size, status, review_notes, uploaded_at "
                        "FROM D4_DOCUMENTS WHERE query_id = ? ORDER BY uploaded_at DESC", [query_id])
    meetings = ctx.db.query(
        "SELECT M.meeting_id, M.meeting_date AS date, M.start_time, M.end_time, M.status, T.name AS tic_name "
        "FROM D5_MEETINGS M JOIN USERS T ON T.user_id = M.assigned_tic WHERE M.query_id = ? ORDER BY M.meeting_date",
        [query_id])
    timeline = ctx.db.query(
        "SELECT A.action_type, A.timestamp, U.name AS by_name FROM D7_AUDIT_LOGS A LEFT JOIN USERS U "
        "ON U.user_id = A.user_id WHERE A.entity = 'Query' AND A.entity_id = ? ORDER BY A.timestamp", [query_id])
    if user["role_name"] == "Student":
        q.pop("student_email", None)
    return {"query": q, "documents": docs, "meetings": meetings, "timeline": timeline}


# ------------------------------------------------------------------------------ student: documents (UC-05)
MAGIC = {"PDF": [b"%PDF"], "PNG": [b"\x89PNG\r\n\x1a\n"], "JPG": [b"\xff\xd8\xff"], "JPEG": [b"\xff\xd8\xff"]}


@app.post("/api/student/queries/{query_id}/documents")
def upload_doc(query_id: str, file: UploadFile = File(...), user=Depends(student_only), ctx=Depends(get_ctx)):
    q = load_query(ctx, user, query_id)
    if q["status"] != "Documents Required":
        raise HTTPException(409, "State Error: No document has been requested for this query")
    f = file.file
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    ext = (file.filename or "").rsplit(".", 1)[-1].upper() if "." in (file.filename or "") else ""
    head = f.read(8)
    f.seek(0)
    if ext in MAGIC and size > 0 and not any(head.startswith(m) for m in MAGIC[ext]):
        raise HTTPException(400, "Validation Failed: File content does not match its extension")
    file_obj = SimpleNamespace(name=file.filename or "", size=size, stream=f)
    return ok(upload_document(ctx, user["user_id"], query_id, file_obj))


@app.get("/api/documents/{document_id}/download")
def download_doc(document_id: str, user=Depends(any_user), ctx=Depends(get_ctx)):
    rows = ctx.db.query("SELECT query_id, file_name, file_type, storage_key FROM D4_DOCUMENTS "
                        "WHERE document_id = ?", [document_id])
    if not rows:
        raise HTTPException(404, "Database Error: Document not found")
    load_query(ctx, user, rows[0]["query_id"])          # enforces ownership / assignment
    audit(ctx, user["user_id"], "Download Document", "Document", document_id)
    storage = S.gw.storage
    if hasattr(storage, "presigned_url"):
        return RedirectResponse(storage.presigned_url(rows[0]["storage_key"]))
    media = {"PDF": "application/pdf", "PNG": "image/png", "JPG": "image/jpeg", "JPEG": "image/jpeg"}
    return FileResponse(storage.path_for(rows[0]["storage_key"]), filename=rows[0]["file_name"],
                        media_type=media.get(rows[0]["file_type"], "application/octet-stream"))


# ------------------------------------------------------------------------------ student: meetings (UC-06)
@app.get("/api/student/queries/{query_id}/slots")
def student_slots(query_id: str, date: str = Query(...), user=Depends(student_only), ctx=Depends(get_ctx)):
    q = load_query(ctx, user, query_id)
    if not q["assigned_tic"]:
        raise HTTPException(409, "State Error: A teacher has not been assigned to this query yet")
    res = view_request_slot_and_accept_meeting(ctx, user["user_id"], "ViewSlots",
                                               {"tic_id": q["assigned_tic"], "target_date": date})
    return {"tic_name": q["tic_name"], "slots": ok(res)["data"]}


@app.post("/api/student/slots/request")
def request_slot(body: SlotRequestBody, user=Depends(student_only), ctx=Depends(get_ctx)):
    load_query(ctx, user, body.query_id)
    res = view_request_slot_and_accept_meeting(ctx, user["user_id"], "RequestSlot",
                                               {"slot_id": body.slot_id, "query_id": body.query_id})
    out = ok(res)
    ctx.db.update("UPDATE D6_TIME_SLOTS SET query_id = ? WHERE slot_id = ?", [body.query_id, body.slot_id])
    return out


@app.get("/api/student/meetings")
def student_meetings(user=Depends(student_only), ctx=Depends(get_ctx)):
    meetings = ctx.db.query(
        "SELECT M.meeting_id, M.query_id, M.meeting_date AS date, M.start_time, M.end_time, M.status, T.name AS tic_name "
        "FROM D5_MEETINGS M JOIN USERS T ON T.user_id = M.assigned_tic WHERE M.student_id = ? "
        "ORDER BY M.meeting_date DESC, M.start_time", [user["user_id"]])
    requests = ctx.db.query(
        "SELECT S.slot_id, S.query_id, S.slot_date AS date, S.start_time, S.end_time, S.status, T.name AS tic_name "
        "FROM D6_TIME_SLOTS S JOIN USERS T ON T.user_id = S.assigned_tic WHERE S.student_id = ? AND S.status = 'Requested' "
        "ORDER BY S.slot_date", [user["user_id"]])
    return {"meetings": meetings, "pending_requests": requests}


# ------------------------------------------------------------------------------ notifications
@app.get("/api/notifications")
def notifications(user=Depends(any_user), ctx=Depends(get_ctx)):
    rows = ctx.db.query(
        "SELECT notification_id, event_type, message, related_query_id, related_document_id, related_meeting_id, "
        "is_read, created_at FROM NOTIFICATIONS WHERE recipient_id = ? ORDER BY created_at DESC LIMIT 50",
        [user["user_id"]])
    return {"unread": sum(1 for r in rows if not r["is_read"]), "items": rows}


@app.post("/api/notifications/read-all")
def read_all(user=Depends(any_user), ctx=Depends(get_ctx)):
    ctx.db.update("UPDATE NOTIFICATIONS SET is_read = TRUE, read_at = now() WHERE recipient_id = ? AND NOT is_read",
                  [user["user_id"]])
    return {"message": "All notifications marked as read"}


@app.post("/api/notifications/{nid}/read")
def read_one(nid: str, user=Depends(any_user), ctx=Depends(get_ctx)):
    ctx.db.update("UPDATE NOTIFICATIONS SET is_read = TRUE, read_at = now() WHERE notification_id = ? "
                  "AND recipient_id = ?", [nid, user["user_id"]])
    return {"message": "Marked as read"}


# ------------------------------------------------------------------------------ admin (UC-08/09/10)
@app.get("/api/admin/stats")
def admin_stats(user=Depends(admin_only), ctx=Depends(get_ctx)):
    by_status = {r["status"]: r["n"] for r in ctx.db.query(
        "SELECT status, count(*)::int AS n FROM D3_QUERIES GROUP BY status")}
    kb = ctx.db.query("SELECT count(*)::int AS n FROM D2_KNOWLEDGE WHERE validity_status = 'Active'")[0]["n"]
    ai = ctx.db.query("SELECT response_status, count(*)::int AS n FROM AI_INTERACTIONS GROUP BY response_status")
    return {"by_status": by_status, "active_kb_entries": kb, "ai": {r["response_status"]: r["n"] for r in ai}}


@app.get("/api/admin/queries/new")
def admin_new_queries(user=Depends(admin_only), ctx=Depends(get_ctx)):
    return ok(admin_view_new_queries(ctx, user["user_id"]))


@app.get("/api/admin/queries")
def admin_all_queries(status: Optional[str] = None, q: Optional[str] = None, user=Depends(admin_only),
                      ctx=Depends(get_ctx)):
    sql = ("SELECT Q.query_id, Q.description, Q.category, Q.status, Q.updated_at, S.name AS student_name, "
           "T.name AS tic_name FROM D3_QUERIES Q JOIN USERS S ON S.user_id = Q.student_id "
           "LEFT JOIN USERS T ON T.user_id = Q.assigned_tic WHERE 1 = 1")
    params: list = []
    if status:
        sql += " AND Q.status = ?"
        params.append(status)
    if q:
        sql += " AND Q.description ILIKE ?"
        params.append(f"%{q}%")
    return ctx.db.query(sql + " ORDER BY Q.updated_at DESC LIMIT 200", params)


@app.post("/api/admin/queries/{query_id}/resolve")
def admin_resolve(query_id: str, body: ResolveBody, user=Depends(admin_only), ctx=Depends(get_ctx)):
    return ok(admin_resolve_query(ctx, user["user_id"], query_id, body.resolution.strip(), body.add_to_kb))


@app.post("/api/admin/queries/{query_id}/forward")
def admin_forward(query_id: str, body: ForwardBody, user=Depends(admin_only), ctx=Depends(get_ctx)):
    res = ok(forward_query_to_tic(ctx, user["user_id"], query_id, body.tic_id))
    ctx.db.insert("INSERT INTO QUERY_ASSIGNMENTS (query_id, assigned_to, assigned_by, department_id) "
                  "SELECT ?, ?, ?, department_id FROM USERS WHERE user_id = ?",
                  [query_id, body.tic_id, user["user_id"], body.tic_id])
    return res


@app.get("/api/admin/queries/{query_id}/tic-suggestions")
def tic_suggestions(query_id: str, user=Depends(admin_only), ctx=Depends(get_ctx)):
    q = load_query(ctx, user, query_id)
    rows = ctx.db.query(
        "SELECT U.user_id, U.name, U.department_id, D.department_name, "
        "(SELECT count(*)::int FROM D3_QUERIES X WHERE X.assigned_tic = U.user_id AND X.status <> 'Resolved') "
        "AS open_queries FROM USERS U JOIN ROLE R ON R.role_id = U.role_id "
        "LEFT JOIN DEPARTMENTS D ON D.dept_id = U.department_id WHERE R.role_name = 'TIC' AND U.is_active "
        "ORDER BY (U.department_id = ?) DESC, open_queries ASC, U.name", [q["department_id"]])
    for i, r in enumerate(rows):
        r["suggested"] = i == 0 and r["department_id"] == q["department_id"]
    return rows


# ------------------------------------------------------------------------------ knowledge base (UC-11)
def kb_role(ctx, user_id):
    rows = ctx.db.query(KB_ROLE_SQL, [user_id])
    return rows[0]["role_name"] if rows else None


@app.get("/api/kb")
def kb_list(q: Optional[str] = None, status: Optional[str] = None, user=Depends(kb_user), ctx=Depends(get_ctx)):
    if kb_role(ctx, user["user_id"]) not in ("Admin", "Authorized TIC"):
        raise HTTPException(403, "Security Error: Unauthorized modification attempt")
    sql = ("SELECT kb_id, title, content, category, source, verification_status, validity_status, version, "
           "updated_at FROM D2_KNOWLEDGE WHERE 1 = 1")
    params: list = []
    if status:
        sql += " AND validity_status = ?"
        params.append(status)
    if q:
        sql += " AND (title ILIKE ? OR content ILIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    return ctx.db.query(sql + " ORDER BY updated_at DESC LIMIT 300", params)


@app.post("/api/kb")
def kb_create(body: KbBody, user=Depends(kb_user), ctx=Depends(get_ctx)):
    res = ok(knowledge_base_management(ctx, user["user_id"], "Create", body.model_dump()))
    audit(ctx, user["user_id"], "Create", "Knowledge Base", res["data"]["kb_id"])
    return res


@app.put("/api/kb/{kb_id}")
def kb_update(kb_id: str, body: KbUpdateBody, user=Depends(kb_user), ctx=Depends(get_ctx)):
    cur = ctx.db.query("SELECT kb_id, title, content, category, source, version, created_by FROM D2_KNOWLEDGE "
                       "WHERE kb_id = ?", [kb_id])
    if not cur:
        raise HTTPException(404, "Database Error: Knowledge Base entry not found")
    c = cur[0]
    merged = {"kb_id": kb_id, "title": body.title or c["title"], "content": body.content or c["content"],
              "category": body.category if body.category is not None else c["category"],
              "source": body.source if body.source is not None else c["source"]}
    changed = merged["content"] != c["content"] or merged["title"] != c["title"]
    if changed and kb_role(ctx, user["user_id"]) in ("Admin", "Authorized TIC"):
        ctx.db.insert("INSERT INTO D2_KNOWLEDGE_VERSIONS (kb_id, version, title, content, category, source, "
                      "changed_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      [kb_id, c["version"], c["title"], c["content"], c["category"], c["source"], user["user_id"]])
    res = ok(knowledge_base_management(ctx, user["user_id"], "Update", merged))
    if changed:
        ctx.db.update("UPDATE D2_KNOWLEDGE SET version = version + 1 WHERE kb_id = ?", [kb_id])
    audit(ctx, user["user_id"], "Update", "Knowledge Base", kb_id)
    return res


@app.post("/api/kb/{kb_id}/deactivate")
def kb_deactivate(kb_id: str, user=Depends(kb_user), ctx=Depends(get_ctx)):
    res = ok(knowledge_base_management(ctx, user["user_id"], "Deactivate", {"kb_id": kb_id}))
    audit(ctx, user["user_id"], "Deactivate", "Knowledge Base", kb_id)
    return res


@app.post("/api/kb/{kb_id}/archive")
def kb_archive(kb_id: str, user=Depends(kb_user), ctx=Depends(get_ctx)):
    if kb_role(ctx, user["user_id"]) not in ("Admin", "Authorized TIC"):
        raise HTTPException(403, "Security Error: Unauthorized modification attempt")
    if ctx.db.update("UPDATE D2_KNOWLEDGE SET validity_status = 'Archived', updated_at = now() WHERE kb_id = ?",
                     [kb_id]) == 0:
        raise HTTPException(404, "Database Error: Knowledge Base entry not found")
    audit(ctx, user["user_id"], "Archive", "Knowledge Base", kb_id)
    return {"message": "Knowledge Base entry archived"}


@app.get("/api/admin/audit")
def audit_log(limit: int = Query(100, le=500), action: Optional[str] = None, user=Depends(admin_only),
              ctx=Depends(get_ctx)):
    sql = ("SELECT A.audit_id, A.user_id, COALESCE(U.name, A.user_id) AS user_name, A.action_type, A.entity, "
           "A.entity_id, A.details, A.timestamp FROM D7_AUDIT_LOGS A LEFT JOIN USERS U ON U.user_id = A.user_id")
    params: list = []
    if action:
        sql += " WHERE A.action_type ILIKE ?"
        params.append(f"%{action}%")
    return ctx.db.query(sql + " ORDER BY A.timestamp DESC, A.audit_id DESC LIMIT ?", params + [limit])


# ------------------------------------------------------------------------------ TIC (UC-12..17)
@app.get("/api/tic/queries")
def tic_queries(user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(tic_view_assigned_queries(ctx, user["user_id"]))


@app.post("/api/tic/queries/{query_id}/resolve")
def tic_resolve(query_id: str, body: ResolveBody, user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(tic_resolve_query(ctx, user["user_id"], query_id, body.resolution.strip(), body.add_to_kb))


@app.post("/api/tic/queries/{query_id}/request-document")
def tic_req_doc(query_id: str, body: DocRequestBody, user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(tic_request_document(ctx, user["user_id"], query_id, body.note.strip()))


@app.post("/api/tic/queries/{query_id}/documents/{doc_id}/review")
def tic_review(query_id: str, doc_id: str, body: ReviewBody, user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(tic_review_document(ctx, user["user_id"], query_id, doc_id, body.decision, body.notes))


@app.get("/api/tic/timetable")
def tic_timetable(date: str = Query(...), user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(view_timetable_availability(ctx, user["user_id"], date))


def _within_free_period(ctx, tic_id, date, start, end) -> bool:
    try:
        periods = ctx.gw.timetable.fetch(tic_id, date)
    except NetworkException:
        raise HTTPException(503, "System Error: External timetable service is temporarily unavailable")
    return any(p["start_time"] <= start and end <= p["end_time"] for p in periods)


def _check_times(date, start, end):
    import datetime as dt
    try:
        dt.date.fromisoformat(date)
        s, e = dt.time.fromisoformat(start), dt.time.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "Validation Failed: Invalid meeting date/time format")
    if e <= s:
        raise HTTPException(400, "Validation Failed: End time must be after start time")


@app.get("/api/tic/slots")
def tic_slots(date: Optional[str] = None, user=Depends(tic_only), ctx=Depends(get_ctx)):
    sql = ("SELECT S.slot_id, S.slot_date AS date, S.start_time, S.end_time, S.status, S.query_id, "
           "St.name AS student_name FROM D6_TIME_SLOTS S LEFT JOIN USERS St ON St.user_id = S.student_id "
           "WHERE S.assigned_tic = ? AND S.slot_date >= CURRENT_DATE")
    params: list = [user["user_id"]]
    if date:
        sql = sql.replace("S.slot_date >= CURRENT_DATE", "S.slot_date = ?")
        params.append(date)
    return ctx.db.query(sql + " ORDER BY S.slot_date, S.start_time", params)


@app.post("/api/tic/slots")
def tic_create_slot(body: SlotCreateBody, user=Depends(tic_only), ctx=Depends(get_ctx)):
    _check_times(body.date, body.start_time, body.end_time)
    if not _within_free_period(ctx, user["user_id"], body.date, body.start_time, body.end_time):
        raise HTTPException(409, "State Error: That time is outside your free timetable periods")
    busy = ctx.db.query("SELECT meeting_id FROM D5_MEETINGS WHERE assigned_tic = ? AND meeting_date = ? "
                        "AND status != 'Cancelled' AND start_time < ? AND end_time > ?",
                        [user["user_id"], body.date, body.end_time, body.start_time])
    if busy:
        raise HTTPException(409, "Concurrency Error: Time slot has already been booked")
    slot_id = new_id()
    try:
        ctx.db.insert("INSERT INTO D6_TIME_SLOTS (slot_id, assigned_tic, slot_date, start_time, end_time) "
                      "VALUES (?, ?, ?, ?, ?)", [slot_id, user["user_id"], body.date, body.start_time, body.end_time])
    except DatabaseException:
        raise HTTPException(409, "State Error: You already published a slot at that time")
    audit(ctx, user["user_id"], "Create Slot", "Slot", slot_id)
    return {"message": "Slot published", "slot_id": slot_id}


@app.post("/api/tic/slots/{slot_id}/accept")
def tic_accept_slot(slot_id: str, user=Depends(tic_only), ctx=Depends(get_ctx)):
    slot = ctx.db.query("SELECT slot_date, start_time, end_time, student_id, query_id FROM D6_TIME_SLOTS "
                        "WHERE slot_id = ? AND assigned_tic = ?", [slot_id, user["user_id"]])
    if slot:
        s = slot[0]
        busy = ctx.db.query("SELECT meeting_id FROM D5_MEETINGS WHERE assigned_tic = ? AND meeting_date = ? "
                            "AND status != 'Cancelled' AND start_time < ? AND end_time > ?",
                            [user["user_id"], s["slot_date"], s["end_time"], s["start_time"]])
        if busy:
            raise HTTPException(409, "Concurrency Error: Time slot has already been booked")
    res = ok(view_request_slot_and_accept_meeting(ctx, user["user_id"], "AcceptMeeting", {"slot_id": slot_id}))
    if slot and slot[0]["student_id"]:
        s = slot[0]
        try:   # mirror the accepted slot into D5 so timetable availability and dashboards stay consistent
            ctx.db.insert("INSERT INTO D5_MEETINGS (meeting_id, query_id, assigned_tic, student_id, meeting_date, "
                          "start_time, end_time, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'Scheduled', now())",
                          [new_id(), s["query_id"], user["user_id"], s["student_id"], s["slot_date"],
                           s["start_time"], s["end_time"]])
        except DatabaseException as exc:
            log.warning("could not mirror accepted slot into meetings: %s", exc)
    return res


@app.get("/api/tic/meetings")
def tic_meetings(user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ctx.db.query(
        "SELECT M.meeting_id, M.query_id, M.meeting_date AS date, M.start_time, M.end_time, M.status, "
        "S.name AS student_name FROM D5_MEETINGS M JOIN USERS S ON S.user_id = M.student_id "
        "WHERE M.assigned_tic = ? ORDER BY M.meeting_date DESC, M.start_time", [user["user_id"]])


@app.post("/api/tic/meetings")
def tic_schedule(body: MeetingBody, user=Depends(tic_only), ctx=Depends(get_ctx)):
    _check_times(body.date, body.start_time, body.end_time)
    if not _within_free_period(ctx, user["user_id"], body.date, body.start_time, body.end_time):
        raise HTTPException(409, "State Error: That time is outside your free timetable periods")
    return ok(manage_meeting(ctx, user["user_id"], "Schedule", body.model_dump()))


@app.post("/api/tic/meetings/{meeting_id}/cancel")
def tic_cancel(meeting_id: str, user=Depends(tic_only), ctx=Depends(get_ctx)):
    return ok(manage_meeting(ctx, user["user_id"], "Cancel", {"meeting_id": meeting_id}))
