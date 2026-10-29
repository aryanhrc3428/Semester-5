"""UC-07 DispatchNotification, UC-08 AdminViewNewQueries, UC-09 AdminResolveQuery,
UC-10 ForwardQueryToTIC, UC-11 KnowledgeBaseManagement."""
import pytest
from types import SimpleNamespace as NS

from app.core import SystemException, success
from app.usecases.admin import (admin_resolve_query, admin_view_new_queries, forward_query_to_tic,
                                knowledge_base_management as kb)
from app.usecases.notify import VALID_EVENTS, dispatch_notification
from .helpers import DB_ERR, NET_ERR, FakeDb, Seq, make_ctx, role


# ======================================================================= UC-07
class Mail:
    def __init__(self, *outcomes):
        self.outcomes, self.sent = list(outcomes or [200]), []

    def send(self, to, subject, body):
        o = self.outcomes[min(len(self.sent), len(self.outcomes) - 1)]
        self.sent.append((to, subject, body))
        if isinstance(o, Exception):
            raise o
        return NS(status_code=o)


@pytest.mark.parametrize("args,expected", [
    ((None, "Query Resolved", "Q1"), "Validation Failed: Inputs cannot be null"),
    (("Admin", None, "Q1"), "Validation Failed: Inputs cannot be null"),
    (("Admin", "Query Resolved", None), "Validation Failed: Inputs cannot be null"),
    ((5, "Query Resolved", "Q1"), "Validation Failed: Invalid data types"),
    (("Admin", 5, "Q1"), "Validation Failed: Invalid data types"),
    (("Admin", "Free Pizza", "Q1"), "Validation Failed: Unrecognized event type"),
])
def test_uc7_validation(args, expected):
    assert dispatch_notification(make_ctx(FakeDb(), email=Mail()), *args).message == expected


@pytest.mark.parametrize("event", VALID_EVENTS)
def test_uc7_every_documented_event_is_accepted(event):
    db = FakeDb().on("WHERE user_id", [{"email": "a@x.edu"}])
    assert dispatch_notification(make_ctx(db, email=Mail()), "U1", event, "REF").is_success


@pytest.mark.parametrize("target,fragment,params", [
    ("Admin", "WHERE R.role_name = ?", ["Admin"]), ("TIC", "WHERE R.role_name = ?", ["TIC"]),
    ("Staff", "IN ('Admin', 'TIC')", []),
])
def test_uc7_role_targets_resolve_all_members(target, fragment, params):
    db = FakeDb().on("ROLE R", [{"email": "a@x.edu"}, {"email": "b@x.edu"}])
    mail = Mail()
    r = dispatch_notification(make_ctx(db, email=mail), target, "Query Assigned", "Q1")
    assert r.message == "Dispatched 2 notifications. Failures: 0"
    assert fragment in db.calls[0][1] and db.calls[0][2] == params
    assert mail.sent[0][1] == "System Notification: Query Assigned"
    assert mail.sent[0][2] == "An event 'Query Assigned' has occurred concerning reference ID: Q1. Please log in to your dashboard to view details."


def test_uc7_resolution_failures():
    assert dispatch_notification(make_ctx(FakeDb().on("USERS", DB_ERR), email=Mail()), "U1", "Query Resolved", "Q").message == "Database Error: Failed to resolve target email addresses"
    for target in ("U1", "Admin"):
        r = dispatch_notification(make_ctx(FakeDb().on("USERS", []), email=Mail()), target, "Query Resolved", "Q")
        assert r.message == "Resolution Error: No valid email addresses found for target"


def test_uc7_audit_log_for_each_success_and_failure_counts():
    db = FakeDb().on("ROLE R", [{"email": "a@x"}, {"email": "b@x"}, {"email": "c@x"}])
    mail = Mail(200, 500, NET_ERR)
    ctx = make_ctx(db, email=mail)
    r = dispatch_notification(ctx, "Staff", "Document Uploaded", "D1")
    assert r.message == "Dispatched 1 notifications. Failures: 2"
    assert db.n("INSERT INTO D7_AUDIT_LOGS") == 1 and any("status 500" in l for l in ctx.logs) and any("Network Error" in l for l in ctx.logs)


def test_uc7_all_failed_and_audit_failure_tolerated():
    r = dispatch_notification(make_ctx(FakeDb().on("USERS", [{"email": "a@x"}]), email=Mail(500)), "U1", "Query Resolved", "Q")
    assert r.message == "Dispatch Failed: Unable to send any notifications"
    db = FakeDb().on("USERS", [{"email": "a@x"}]).on("INSERT INTO D7_AUDIT_LOGS", DB_ERR)
    ctx = make_ctx(db, email=Mail(200))
    assert dispatch_notification(ctx, "U1", "Query Resolved", "Q").is_success and any("Failed to log notification success" in l for l in ctx.logs)


# ======================================================================= UC-08
def test_uc8_validation_and_rbac():
    assert admin_view_new_queries(make_ctx(), None).message == "Validation Failed: Admin ID cannot be null"
    assert admin_view_new_queries(make_ctx(), 3).message == "Validation Failed: Invalid data type for Admin ID"
    assert admin_view_new_queries(make_ctx(FakeDb().on("ROLE", [])), "A1").message == "Database Error: Admin identity not found"
    r = admin_view_new_queries(make_ctx(FakeDb().on("ROLE", role("Student"))), "A1")
    assert r.message == "Security Error: Unauthorized access. Admin privileges required." and r.http_status == 403
    assert admin_view_new_queries(make_ctx(FakeDb().on("ROLE", DB_ERR)), "A1").message == "System Error: Unable to validate permissions"


def test_uc8_retrieval_and_empty():
    db = FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", DB_ERR)
    assert admin_view_new_queries(make_ctx(db), "A1").message == "Database Error: Failed to retrieve open queries"
    db = FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", [])
    r = admin_view_new_queries(make_ctx(db), "A1")
    assert r.message == "No new queries found" and r.data == []


def test_uc8_student_details_and_fallbacks():
    qs = [{"query_id": "Q1", "student_id": "S1"}, {"query_id": "Q2", "student_id": "S2"}, {"query_id": "Q3", "student_id": "S3"}]
    db = (FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", qs)
          .on("SELECT name, email FROM USERS", Seq([{"name": "Aarav", "email": "a@x"}], [], DB_ERR)))
    ctx = make_ctx(db)
    r = admin_view_new_queries(ctx, "A1")
    assert db.calls[1][2] == ["Open"]
    assert [x["student_info"] for x in r.data] == [{"name": "Aarav", "email": "a@x"}, {"name": "Unknown Student", "email": "Unknown Email"}, {"name": "Data unavailable", "email": "Data unavailable"}]
    assert ctx.logs


# ======================================================================= UC-09
RES = "Please collect it from the office."


def uc9_db(**routes):
    db = FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", [{"student_id": "S1", "description": "Need bonafide", "category": "Administrative"}])
    for k, v in routes.items():
        db.routes.insert(0, (k.replace("__", " "), v))
    return db


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", RES, False), "Validation Failed: Parameters cannot be null"),
    (("A1", None, RES, False), "Validation Failed: Parameters cannot be null"),
    (("A1", "Q1", None, False), "Validation Failed: Parameters cannot be null"),
    (("A1", "Q1", RES, None), "Validation Failed: Parameters cannot be null"),
    ((1, "Q1", RES, False), "Validation Failed: Invalid parameter data types"),
    (("A1", "Q1", RES, "yes"), "Validation Failed: Invalid parameter data types"),
    (("A1", "Q1", RES, 1), "Validation Failed: Invalid parameter data types"),
    (("A1", "Q1", "short", False), "Validation Failed: Resolution text length out of bounds"),
    (("A1", "Q1", "x" * 5001, False), "Validation Failed: Resolution text length out of bounds"),
])
def test_uc9_validation(args, expected):
    assert admin_resolve_query(make_ctx(uc9_db()), *args).message == expected


def test_uc9_rbac_and_query_checks():
    for rows in ([], role("Student")):
        r = admin_resolve_query(make_ctx(FakeDb().on("ROLE", rows)), "A1", "Q1", RES, False)
        assert r.message == "Security Error: Unauthorized access. Admin privileges required."
    assert admin_resolve_query(make_ctx(FakeDb().on("ROLE", DB_ERR)), "A1", "Q1", RES, False).message == "System Error: Unable to validate permissions"
    db = FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", [])
    r = admin_resolve_query(make_ctx(db), "A1", "Q1", RES, False)
    assert r.message == "Database Error: Target query reference not found" and r.http_status == 404
    db = FakeDb().on("ROLE", role("Admin")).on("FROM D3_QUERIES", DB_ERR)
    assert admin_resolve_query(make_ctx(db), "A1", "Q1", RES, False).message == "System Error: Unable to validate query reference"


def test_uc9_resolves_audits_and_notifies_student():
    db = uc9_db()
    ctx = make_ctx(db)
    r = admin_resolve_query(ctx, "A1", "Q1", RES, False)
    assert r.message == "Query successfully resolved" and r.data == {"query_id": "Q1"}
    assert db.events == ["begin", "commit"] and ctx.sent == [("S1", "Query Resolved", "Q1")]
    assert [c for c in db.calls if "UPDATE D3_QUERIES" in c[1]][0][2][:3] == ["Resolved", RES, "A1"]


@pytest.mark.parametrize("failing", ["UPDATE D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc9_transaction_failure(failing):
    db = uc9_db(**{failing: DB_ERR})
    ctx = make_ctx(db)
    r = admin_resolve_query(ctx, "A1", "Q1", RES, True)
    assert r.message == "Database Error: Failed to resolve query and commit audit log"
    assert db.events == ["begin", "rollback"] and ctx.sent == []


def test_uc9_kb_escalation_payload_and_isolation():
    calls = []
    ctx = make_ctx(uc9_db())
    ctx.kb_manage = lambda c, who, action, payload: calls.append((who, action, payload)) or success("ok", {"kb_id": "K"})
    assert admin_resolve_query(ctx, "A1", "Q1", RES, True).is_success
    assert calls == [("A1", "Create", {"title": "Need bonafide", "content": RES, "category": "Administrative", "source": "Admin Resolution"})]
    ctx2 = make_ctx(uc9_db())
    ctx2.kb_manage = lambda *a: calls.append("no") if False else None
    admin_resolve_query(ctx2, "A1", "Q1", RES, False)
    assert len(calls) == 1                                         # flag false -> no KB call


def test_uc9_kb_failures_never_fail_resolution():
    def boom(*a):
        raise SystemException("kb down")
    ctx = make_ctx(uc9_db())
    ctx.kb_manage = boom
    assert admin_resolve_query(ctx, "A1", "Q1", RES, True).is_success and any("Knowledge Base" in l for l in ctx.logs)
    from app.core import err
    ctx = make_ctx(uc9_db())
    ctx.kb_manage = lambda *a: err("Security Error: Unauthorized modification attempt")
    assert admin_resolve_query(ctx, "A1", "Q1", RES, True).is_success and any("Knowledge Base" in l for l in ctx.logs)


def test_uc9_notification_failure_non_blocking():
    ctx = make_ctx(uc9_db(), dispatch_raises=True)
    assert admin_resolve_query(ctx, "A1", "Q1", RES, False).is_success


# ======================================================================= UC-10
def uc10_db(tic_role=None, **routes):
    db = FakeDb().on("ROLE", lambda p: role("Admin") if p[0] == "A1" else (tic_role if tic_role is not None else role("TIC")))
    db.on("FROM D3_QUERIES", [{"status": "Open"}])
    for k, v in routes.items():
        db.routes.insert(0, (k.replace("__", " "), v))
    return db


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", "T1"), "Validation Failed: Parameters cannot be null"), (("A1", None, "T1"), "Validation Failed: Parameters cannot be null"),
    (("A1", "Q1", None), "Validation Failed: Parameters cannot be null"), ((1, "Q1", "T1"), "Validation Failed: Invalid parameter data types"),
    (("A1", 1, "T1"), "Validation Failed: Invalid parameter data types"), (("A1", "Q1", 1), "Validation Failed: Invalid parameter data types"),
])
def test_uc10_validation(args, expected):
    assert forward_query_to_tic(make_ctx(uc10_db()), *args).message == expected


def test_uc10_authorisation_chain():
    assert forward_query_to_tic(make_ctx(FakeDb().on("ROLE", role("TIC"))), "A1", "Q1", "T1").message == "Security Error: Unauthorized access. Admin privileges required."
    assert forward_query_to_tic(make_ctx(FakeDb().on("ROLE", DB_ERR)), "A1", "Q1", "T1").message == "System Error: Unable to validate caller permissions"
    r = forward_query_to_tic(make_ctx(uc10_db(tic_role=[])), "A1", "Q1", "T1")
    assert r.message == "Database Error: Target user identity not found"
    r = forward_query_to_tic(make_ctx(uc10_db(tic_role=role("Student"))), "A1", "Q1", "T1")
    assert r.message == "Security Error: Cannot assign query. Target user is not a Teacher-in-Charge."
    db = FakeDb().on("ROLE", Seq(role("Admin"), DB_ERR))
    assert forward_query_to_tic(make_ctx(db), "A1", "Q1", "T1").message == "System Error: Unable to validate target user role"


def test_uc10_query_checks_and_transaction():
    assert forward_query_to_tic(make_ctx(uc10_db(FROM__D3_QUERIES=[])), "A1", "Q1", "T1").message == "Database Error: Target query reference not found"
    assert forward_query_to_tic(make_ctx(uc10_db(FROM__D3_QUERIES=DB_ERR)), "A1", "Q1", "T1").message == "System Error: Unable to validate query reference"
    db = uc10_db()
    ctx = make_ctx(db)
    r = forward_query_to_tic(ctx, "A1", "Q1", "T1")
    assert r.message == "Query successfully forwarded to TIC" and ctx.sent == [("T1", "Query Assigned", "Q1")]
    assert [c for c in db.calls if "UPDATE D3_QUERIES" in c[1]][0][2][:2] == ["T1", "Assigned to TIC"]
    for failing in ("UPDATE D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"):
        db = uc10_db(**{failing: DB_ERR})
        assert forward_query_to_tic(make_ctx(db), "A1", "Q1", "T1").message == "Database Error: Failed to assign query and commit audit log" and db.events[-1] == "rollback"
    assert forward_query_to_tic(make_ctx(uc10_db(), dispatch_raises=True), "A1", "Q1", "T1").is_success


# ======================================================================= UC-11
class Emb:
    def __init__(self, vec=(0.1, 0.2), exc=None):
        self.vec, self.exc, self.n = list(vec) if vec is not None else None, exc, 0

    def generate_embedding(self, text, task="RETRIEVAL_DOCUMENT"):
        self.n += 1
        if self.exc:
            raise self.exc
        return self.vec


def kb_ctx(role_rows=None, emb=None, **routes):
    db = FakeDb()
    for k, v in routes.items():
        db.on(k.replace("__", " "), v)
    db.on("kb_permission", role_rows if role_rows is not None else role("Admin"))
    return make_ctx(db, embedder=emb or Emb())


@pytest.mark.parametrize("args,expected", [
    ((None, "Create", {}), "Validation Failed: Base parameters cannot be null"), (("A1", None, {}), "Validation Failed: Base parameters cannot be null"),
    (("A1", "Create", None), "Validation Failed: Base parameters cannot be null"), (("A1", 5, {}), "Validation Failed: Invalid parameter data types"),
    (("A1", "Create", "text"), "Validation Failed: Invalid parameter data types"), (("A1", "Delete", {}), "Validation Failed: Unrecognized action type"),
])
def test_uc11_validation(args, expected):
    assert kb(kb_ctx(), *args).message == expected


def test_uc11_rbac():
    assert kb(kb_ctx([]), "A1", "Create", {}).message == "Database Error: User identity not found"
    for who in (role("Student"), role("TIC")):
        assert kb(kb_ctx(who), "A1", "Create", {}).message == "Security Error: Unauthorized modification attempt"
    assert kb(kb_ctx(role("Authorized TIC")), "A1", "Create", {"title": None}).message == "Validation Failed: Title and content are required for creation"
    assert kb(kb_ctx(kb_permission=DB_ERR), "A1", "Create", {}).message == "System Error: Unable to validate permissions"


def test_uc11_create():
    emb = Emb()
    ctx = kb_ctx(emb=emb)
    r = kb(ctx, "A1", "Create", {"title": "T", "content": "C", "category": "Academic", "source": "S"})
    assert r.message == "Knowledge Base entry created" and r.data == {"kb_id": "NEW-ID"}
    ins = [c for c in ctx.db.calls if "INSERT INTO D2_KNOWLEDGE" in c[1]][0][2]
    assert ins[5:9] == ["Verified", "Active", [0.1, 0.2], "A1"]
    for field in ("title", "content"):
        d = {"title": "T", "content": "C"}
        d.pop(field)
        assert kb(kb_ctx(), "A1", "Create", d).message == "Validation Failed: Title and content are required for creation"


def test_uc11_create_failures():
    for vec in (None, []):
        assert kb(kb_ctx(emb=Emb(vec)), "A1", "Create", {"title": "T", "content": "C"}).message == "API Error: Failed to generate vector embedding"
    assert kb(kb_ctx(emb=Emb(exc=NET_ERR)), "A1", "Create", {"title": "T", "content": "C"}).message == "System Error: AI Embedding service unavailable"
    ctx = kb_ctx(INSERT__INTO__D2_KNOWLEDGE=DB_ERR)
    assert kb(ctx, "A1", "Create", {"title": "T", "content": "C"}).message == "Database Error: Failed to insert new KB entry"


def test_uc11_update_regenerates_embedding_only_when_content_changes():
    emb = Emb()
    ctx = kb_ctx(emb=emb, SELECT__content__FROM__D2=[{"content": "old"}])
    r = kb(ctx, "A1", "Update", {"kb_id": "K1", "title": "T", "category": "C", "source": "S", "content": "new"})
    assert r.message == "Knowledge Base entry updated" and emb.n == 1
    upd = [c for c in ctx.db.calls if c[0] == "update"][0]
    assert ", content = ?, embedding = ?" in upd[1] and upd[2][-1] == "K1"
    for same in ({"kb_id": "K1", "title": "T", "content": "old"}, {"kb_id": "K1", "title": "T"}):
        emb2 = Emb()
        ctx = kb_ctx(emb=emb2, SELECT__content__FROM__D2=[{"content": "old"}])
        assert kb(ctx, "A1", "Update", same).is_success and emb2.n == 0
        assert "embedding" not in [c for c in ctx.db.calls if c[0] == "update"][0][1]


def test_uc11_update_guards_and_failures():
    assert kb(kb_ctx(), "A1", "Update", {}).message == "Validation Failed: KB ID required for update"
    assert kb(kb_ctx(SELECT__content__FROM__D2=[]), "A1", "Update", {"kb_id": "K"}).message == "Database Error: Knowledge Base entry not found"
    assert kb(kb_ctx(SELECT__content__FROM__D2=DB_ERR), "A1", "Update", {"kb_id": "K"}).message == "Database Error: Failed to update KB entry"
    ctx = kb_ctx(SELECT__content__FROM__D2=[{"content": "old"}], UPDATE__D2_KNOWLEDGE=DB_ERR)
    assert kb(ctx, "A1", "Update", {"kb_id": "K"}).message == "Database Error: Failed to update KB entry"
    ctx = kb_ctx(emb=Emb(exc=NET_ERR), SELECT__content__FROM__D2=[{"content": "old"}])
    assert kb(ctx, "A1", "Update", {"kb_id": "K", "content": "new"}).message == "System Error: AI Embedding service unavailable during update"


def test_uc11_deactivate():
    assert kb(kb_ctx(), "A1", "Deactivate", {}).message == "Validation Failed: KB ID required for deactivation"
    ctx = kb_ctx(UPDATE__D2_KNOWLEDGE=1)
    r = kb(ctx, "A1", "Deactivate", {"kb_id": "K1"})
    assert r.message == "Knowledge Base entry deactivated" and r.data == {"kb_id": "K1"}
    assert kb(kb_ctx(UPDATE__D2_KNOWLEDGE=0), "A1", "Deactivate", {"kb_id": "K1"}).message == "Database Error: Target entry not found or already inactive"
    assert kb(kb_ctx(UPDATE__D2_KNOWLEDGE=DB_ERR), "A1", "Deactivate", {"kb_id": "K1"}).message == "Database Error: Failed to deactivate KB entry"
