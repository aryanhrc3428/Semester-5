"""UC-12 TICViewAssignedQueries, UC-13 TICResolveQuery, UC-14 TICRequestDocument,
UC-15 TICReviewDocument, UC-16 ViewTimetableAvailability, UC-17 ManageMeeting."""
import pytest

from app.core import SystemException, err, success
from app.usecases.tic import (manage_meeting, tic_request_document, tic_resolve_query, tic_review_document,
                              tic_view_assigned_queries, view_timetable_availability)
from .helpers import DB_ERR, NET_ERR, FakeDb, Seq, make_ctx, role


def db_with(role_rows, **routes):
    db = FakeDb().on("ROLE", role_rows)
    for k, v in routes.items():
        db.on(k.replace("__", " "), v)
    return db


def put_first(db, fragment, value):
    db.routes.insert(0, (fragment, value))
    return db


# ======================================================================= UC-12
def test_uc12_validation_and_rbac():
    assert tic_view_assigned_queries(make_ctx(), None).message == "Validation Failed: TIC ID cannot be null"
    assert tic_view_assigned_queries(make_ctx(), 4).message == "Validation Failed: Invalid data type for TIC ID"
    assert tic_view_assigned_queries(make_ctx(db_with([])), "T1").message == "Database Error: User identity not found"
    r = tic_view_assigned_queries(make_ctx(db_with(role("Admin"))), "T1")
    assert r.message == "Security Error: Unauthorized access. TIC privileges required." and r.http_status == 403
    assert tic_view_assigned_queries(make_ctx(db_with(DB_ERR)), "T1").message == "System Error: Unable to validate permissions"


def test_uc12_retrieval_and_aggregation():
    assert tic_view_assigned_queries(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=DB_ERR)), "T1").message == "Database Error: Failed to retrieve assigned queries"
    r = tic_view_assigned_queries(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=[])), "T1")
    assert r.message == "No assigned queries found" and r.data == []
    qs = [{"query_id": "Q1", "student_id": "S1"}, {"query_id": "Q2", "student_id": "S2"}, {"query_id": "Q3", "student_id": "S3"}]
    db = db_with(role("TIC"), FROM__D3_QUERIES=qs)
    db.on("name, email, department_id", Seq([{"name": "A", "email": "a@x", "department_id": "D1"}], [], DB_ERR))
    ctx = make_ctx(db)
    r = tic_view_assigned_queries(ctx, "T1")
    assert r.message == "TIC dashboard data retrieved successfully"
    assert [x["student_info"]["department_id"] for x in r.data] == ["D1", "Unknown", "Data unavailable"]
    assert db.calls[1][2] == ["T1"] and ctx.logs


# ======================================================================= UC-13
RES = "Resolved by correcting the record."


def tic_q(assigned="T1"):
    return [{"assigned_tic": assigned, "student_id": "S1", "description": "Marks missing", "category": "Academic"}]


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", RES, False), "Validation Failed: Parameters cannot be null"), (("T1", None, RES, False), "Validation Failed: Parameters cannot be null"),
    (("T1", "Q1", None, False), "Validation Failed: Parameters cannot be null"), (("T1", "Q1", RES, None), "Validation Failed: Parameters cannot be null"),
    ((1, "Q1", RES, False), "Validation Failed: Invalid parameter data types"), (("T1", 1, RES, False), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", 5, False), "Validation Failed: Invalid parameter data types"), (("T1", "Q1", RES, "true"), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", "tiny", False), "Validation Failed: Resolution text length out of bounds"),
    (("T1", "Q1", "x" * 5001, False), "Validation Failed: Resolution text length out of bounds"),
])
def test_uc13_validation(args, expected):
    assert tic_resolve_query(make_ctx(db_with(role("TIC"))), *args).message == expected


def test_uc13_rbac_ownership_and_lookup_failures():
    for rows in ([], role("Admin")):
        assert tic_resolve_query(make_ctx(db_with(rows)), "T1", "Q1", RES, False).message == "Security Error: Unauthorized access. TIC privileges required."
    assert tic_resolve_query(make_ctx(db_with(DB_ERR)), "T1", "Q1", RES, False).message == "System Error: Unable to validate permissions"
    assert tic_resolve_query(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=[])), "T1", "Q1", RES, False).message == "Database Error: Target query reference not found"
    r = tic_resolve_query(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=tic_q("T2"))), "T1", "Q1", RES, False)
    assert r.message == "Security Error: Unauthorized. You can only resolve queries explicitly assigned to you." and r.http_status == 403
    assert tic_resolve_query(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=DB_ERR)), "T1", "Q1", RES, False).message == "System Error: Unable to validate query ownership"


def test_uc13_success_kb_and_isolation():
    db = db_with(role("TIC"), FROM__D3_QUERIES=tic_q())
    ctx = make_ctx(db)
    seen = []
    ctx.kb_manage = lambda c, who, action, payload: seen.append((who, action, payload)) or success("ok")
    r = tic_resolve_query(ctx, "T1", "Q1", RES, True)
    assert r.message == "Query successfully resolved" and ctx.sent == [("S1", "Query Resolved", "Q1")]
    assert seen == [("T1", "Create", {"title": "Marks missing", "content": RES, "category": "Academic", "source": "TIC Resolution - T1"})]
    assert [c for c in db.calls if "UPDATE D3_QUERIES" in c[1]][0][2][:3] == ["Resolved", RES, "T1"]

    def boom(*a):
        raise SystemException("down")
    ctx = make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=tic_q()))
    ctx.kb_manage = boom
    assert tic_resolve_query(ctx, "T1", "Q1", RES, True).is_success and ctx.logs
    ctx = make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=tic_q()))
    ctx.kb_manage = lambda *a: err("Security Error: Unauthorized modification attempt")
    assert tic_resolve_query(ctx, "T1", "Q1", RES, True).is_success and ctx.logs
    assert tic_resolve_query(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=tic_q()), dispatch_raises=True), "T1", "Q1", RES, False).is_success


def test_uc13_real_kb_path_denies_plain_tic():
    """Without the KB permission the real UC-11 call is refused, yet resolution still succeeds."""
    db = db_with(role("TIC"), FROM__D3_QUERIES=tic_q())
    ctx = make_ctx(db)
    assert tic_resolve_query(ctx, "T1", "Q1", RES, True).is_success
    assert any("Failed to add resolution to Knowledge Base" in l for l in ctx.logs)


@pytest.mark.parametrize("failing", ["UPDATE D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc13_transaction_failure(failing):
    db = put_first(db_with(role("TIC"), FROM__D3_QUERIES=tic_q()), failing, DB_ERR)
    ctx = make_ctx(db)
    assert tic_resolve_query(ctx, "T1", "Q1", RES, False).message == "Database Error: Failed to resolve query and commit audit log"
    assert db.events == ["begin", "rollback"] and ctx.sent == []


# ======================================================================= UC-14
NOTE = "Upload fee receipt"


def req_q(status="Assigned to TIC", assigned="T1"):
    return [{"assigned_tic": assigned, "student_id": "S1", "status": status}]


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", NOTE), "Validation Failed: Parameters cannot be null"), (("T1", None, NOTE), "Validation Failed: Parameters cannot be null"),
    (("T1", "Q1", None), "Validation Failed: Parameters cannot be null"), ((1, "Q1", NOTE), "Validation Failed: Invalid parameter data types"),
    (("T1", 1, NOTE), "Validation Failed: Invalid parameter data types"), (("T1", "Q1", 1), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", "abcd"), "Validation Failed: Document request note length out of bounds"),
    (("T1", "Q1", "x" * 1001), "Validation Failed: Document request note length out of bounds"),
])
def test_uc14_validation(args, expected):
    assert tic_request_document(make_ctx(db_with(role("TIC"))), *args).message == expected


def test_uc14_guards():
    for rows in ([], role("Student")):
        assert tic_request_document(make_ctx(db_with(rows)), "T1", "Q1", NOTE).message == "Security Error: Unauthorized access. TIC privileges required."
    assert tic_request_document(make_ctx(db_with(DB_ERR)), "T1", "Q1", NOTE).message == "System Error: Unable to validate permissions"
    assert tic_request_document(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=[])), "T1", "Q1", NOTE).message == "Database Error: Target query reference not found"
    assert tic_request_document(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=req_q(assigned="T2"))), "T1", "Q1", NOTE).message == "Security Error: Unauthorized. You can only manage queries explicitly assigned to you."
    for status in ("Resolved", "Closed"):
        r = tic_request_document(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=req_q(status))), "T1", "Q1", NOTE)
        assert r.message == "State Error: Cannot request documents for a closed or resolved query." and r.http_status == 409
    assert tic_request_document(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=DB_ERR)), "T1", "Q1", NOTE).message == "System Error: Unable to validate query ownership and state"


def test_uc14_success_and_failures():
    db = db_with(role("TIC"), FROM__D3_QUERIES=req_q())
    ctx = make_ctx(db)
    r = tic_request_document(ctx, "T1", "Q1", NOTE)
    assert r.message == "Document request successfully logged and student notified"
    assert [c for c in db.calls if "UPDATE D3_QUERIES" in c[1]][0][2][:2] == ["Documents Required", NOTE]
    assert ctx.sent == [("S1", "Document Required", "Q1")]
    for failing in ("UPDATE D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"):
        db = put_first(db_with(role("TIC"), FROM__D3_QUERIES=req_q()), failing, DB_ERR)
        assert tic_request_document(make_ctx(db), "T1", "Q1", NOTE).message == "Database Error: Failed to update query state and commit audit log" and db.events[-1] == "rollback"
    assert tic_request_document(make_ctx(db_with(role("TIC"), FROM__D3_QUERIES=req_q()), dispatch_raises=True), "T1", "Q1", NOTE).is_success


# ======================================================================= UC-15
def review_db(doc_status="Pending Review", owner="T1", **extra):
    db = db_with(role("TIC"), FROM__D4_DOCUMENTS=[{"status": doc_status}])
    db.on("SELECT assigned_tic, student_id FROM D3_QUERIES", [{"assigned_tic": owner, "student_id": "S1"}])
    for k, v in extra.items():
        put_first(db, k.replace("__", " "), v)
    return db


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", "D1", "Accept", None), "Validation Failed: Core parameters cannot be null"),
    (("T1", None, "D1", "Accept", None), "Validation Failed: Core parameters cannot be null"),
    (("T1", "Q1", None, "Accept", None), "Validation Failed: Core parameters cannot be null"),
    (("T1", "Q1", "D1", None, None), "Validation Failed: Core parameters cannot be null"),
    ((1, "Q1", "D1", "Accept", None), "Validation Failed: Invalid parameter data types"),
    (("T1", 1, "D1", "Accept", None), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", 1, "Accept", None), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", "D1", 1, None), "Validation Failed: Invalid parameter data types"),
    (("T1", "Q1", "D1", "Maybe", None), "Validation Failed: Decision must be 'Accept' or 'Reject'"),
    (("T1", "Q1", "D1", "Reject", None), "Validation Failed: Rejection requires detailed review notes"),
    (("T1", "Q1", "D1", "Reject", "no"), "Validation Failed: Rejection requires detailed review notes"),
])
def test_uc15_validation(args, expected):
    assert tic_review_document(make_ctx(review_db()), *args).message == expected


def test_uc15_guards():
    for rows in ([], role("Student")):
        assert tic_review_document(make_ctx(db_with(rows)), "T1", "Q1", "D1", "Accept").message == "Security Error: Unauthorized access. TIC privileges required."
    assert tic_review_document(make_ctx(db_with(DB_ERR)), "T1", "Q1", "D1", "Accept").message == "System Error: Unable to validate permissions"
    assert tic_review_document(make_ctx(review_db(**{"SELECT assigned_tic, student_id FROM D3_QUERIES": []})), "T1", "Q1", "D1", "Accept").message == "Database Error: Target query reference not found"
    assert tic_review_document(make_ctx(review_db(owner="T2")), "T1", "Q1", "D1", "Accept").message == "Security Error: Unauthorized. You can only review documents for queries assigned to you."
    assert tic_review_document(make_ctx(review_db(FROM__D4_DOCUMENTS=[])), "T1", "Q1", "D1", "Accept").message == "Database Error: Document not found or does not belong to the specified query"
    r = tic_review_document(make_ctx(review_db(doc_status="Verified")), "T1", "Q1", "D1", "Accept")
    assert r.message == "State Error: Document is not in a reviewable state" and r.http_status == 409
    assert tic_review_document(make_ctx(review_db(FROM__D4_DOCUMENTS=DB_ERR)), "T1", "Q1", "D1", "Accept").message == "System Error: Unable to validate query and document integrity"


@pytest.mark.parametrize("decision,notes,doc_state,query_state,event,message", [
    ("Accept", None, "Verified", "Assigned to TIC", "Document Accepted", "Document successfully Accepted"),
    ("Accept", "Looks good", "Verified", "Assigned to TIC", "Document Accepted", "Document successfully Accepted"),
    ("Reject", "Blurry scan, please retake", "Rejected", "Documents Required", "Document Rejected", "Document successfully Rejected"),
])
def test_uc15_decisions(decision, notes, doc_state, query_state, event, message):
    db = review_db()
    ctx = make_ctx(db)
    r = tic_review_document(ctx, "T1", "Q1", "D1", decision, notes)
    assert r.message == message and r.data == {"document_id": "D1"} and db.events == ["begin", "commit"]
    updates = [c for c in db.calls if c[0] == "update"]
    assert updates[0][2][:2] == [doc_state, notes] and updates[1][2][0] == query_state
    assert [c for c in db.calls if "D7_AUDIT_LOGS" in c[1]][0][2][1] == "Review Document - " + decision
    assert ctx.sent == [("S1", event, "Q1")]


@pytest.mark.parametrize("failing", ["UPDATE D4_DOCUMENTS", "UPDATE D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc15_transaction_failures(failing):
    db = review_db(**{failing: DB_ERR})
    assert tic_review_document(make_ctx(db), "T1", "Q1", "D1", "Accept").message == "Database Error: Failed to update document and query states" and db.events[-1] == "rollback"
    assert tic_review_document(make_ctx(review_db(), dispatch_raises=True), "T1", "Q1", "D1", "Accept").is_success


# ======================================================================= UC-16
class TT:
    def __init__(self, result=None, exc=None):
        self.result, self.exc = result, exc

    def fetch(self, tic, date):
        if self.exc:
            raise self.exc
        return self.result


P = lambda s, e: {"start_time": s, "end_time": e}  # noqa: E731


def tt_ctx(schedule, booked=None, role_rows=None, exc=None):
    db = db_with(role_rows if role_rows is not None else role("TIC"), FROM__D5_MEETINGS=booked if booked is not None else [])
    return make_ctx(db, timetable=TT(schedule, exc))


@pytest.mark.parametrize("args,expected", [
    ((None, "2026-11-02"), "Validation Failed: Parameters cannot be null"), (("T1", None), "Validation Failed: Parameters cannot be null"),
    ((1, "2026-11-02"), "Validation Failed: Invalid parameter data types"), (("T1", 20261102), "Validation Failed: Invalid parameter data types"),
    (("T1", "2026-1-2"), "Validation Failed: Invalid date format, expected YYYY-MM-DD"),
    (("T1", "2026-11-022"), "Validation Failed: Invalid date format, expected YYYY-MM-DD"),
])
def test_uc16_validation(args, expected):
    assert view_timetable_availability(tt_ctx([]), *args).message == expected


def test_uc16_guards_and_external_failures():
    for rows in ([], role("Student")):
        assert view_timetable_availability(tt_ctx([], role_rows=rows), "T1", "2026-11-02").message == "Security Error: Unauthorized access. TIC privileges required."
    assert view_timetable_availability(tt_ctx([], role_rows=DB_ERR), "T1", "2026-11-02").message == "System Error: Unable to validate permissions"
    assert view_timetable_availability(tt_ctx(None), "T1", "2026-11-02").message == "API Error: Timetable service returned a null schedule"
    ctx = tt_ctx(None, exc=NET_ERR)
    assert view_timetable_availability(ctx, "T1", "2026-11-02").message == "System Error: External timetable service is temporarily unavailable" and ctx.logs
    r = view_timetable_availability(tt_ctx([]), "T1", "2026-11-01")
    assert r.message == "No slots available on this date" and r.data == []
    db = db_with(role("TIC"), FROM__D5_MEETINGS=DB_ERR)
    assert view_timetable_availability(make_ctx(db, timetable=TT([P("09:00", "10:00")])), "T1", "2026-11-02").message == "Database Error: Failed to retrieve existing meeting bookings"


@pytest.mark.parametrize("booked,expected", [
    ([], [("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00")]),
    ([P("10:00", "11:00")], [("09:00", "10:00"), ("11:00", "12:00")]),                      # exact overlap
    ([P("09:30", "10:30")], [("11:00", "12:00")]),                                          # partial overlaps remove two
    ([P("08:00", "09:00"), P("12:00", "13:00")], [("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00")]),   # touching edges do not conflict
    ([P("08:00", "13:00")], []),                                                            # fully covering
])
def test_uc16_conflict_resolution(booked, expected):
    base = [P("09:00", "10:00"), P("10:00", "11:00"), P("11:00", "12:00")]
    ctx = tt_ctx(base, booked)
    r = view_timetable_availability(ctx, "T1", "2026-11-02")
    assert r.message == "Timetable availability calculated successfully"
    assert [(s["start_time"], s["end_time"]) for s in r.data] == expected
    assert ctx.db.calls[1][2] == ["T1", "2026-11-02", "Cancelled"]


# ======================================================================= UC-17
M = {"query_id": "Q1", "date": "2026-11-02", "start_time": "10:00", "end_time": "11:00"}


def mm_db(owner="T1", conflict=None, meeting=None, **extra):
    db = db_with(role("TIC"))
    db.on("SELECT assigned_tic, student_id FROM D3_QUERIES", [{"assigned_tic": owner, "student_id": "S1"}] if owner else [])
    db.on("SELECT meeting_id FROM D5_MEETINGS", conflict or [])
    db.on("SELECT assigned_tic, student_id, status FROM D5_MEETINGS", meeting if meeting is not None else [])
    for k, v in extra.items():
        put_first(db, k.replace("__", " "), v)
    return db


@pytest.mark.parametrize("args,expected", [
    ((None, "Schedule", M), "Validation Failed: Core parameters cannot be null"), (("T1", None, M), "Validation Failed: Core parameters cannot be null"),
    (("T1", "Schedule", None), "Validation Failed: Core parameters cannot be null"), ((1, "Schedule", M), "Validation Failed: Invalid parameter data types"),
    (("T1", 1, M), "Validation Failed: Invalid parameter data types"), (("T1", "Schedule", "x"), "Validation Failed: Invalid parameter data types"),
    (("T1", "Reschedule", M), "Validation Failed: Action must be 'Schedule' or 'Cancel'"),
])
def test_uc17_validation(args, expected):
    assert manage_meeting(make_ctx(mm_db()), *args).message == expected


def test_uc17_rbac_and_incomplete_data():
    for rows in ([], role("Student")):
        assert manage_meeting(make_ctx(db_with(rows)), "T1", "Schedule", M).message == "Security Error: Unauthorized access. TIC privileges required."
    assert manage_meeting(make_ctx(db_with(DB_ERR)), "T1", "Schedule", M).message == "System Error: Unable to validate permissions"
    for missing in ("query_id", "date", "start_time", "end_time"):
        d = dict(M)
        d.pop(missing)
        assert manage_meeting(make_ctx(mm_db()), "T1", "Schedule", d).message == "Validation Failed: Incomplete meeting scheduling data"
    assert manage_meeting(make_ctx(mm_db()), "T1", "Cancel", {}).message == "Validation Failed: Meeting ID required for cancellation"


def test_uc17_schedule_success():
    db = mm_db()
    ctx = make_ctx(db)
    r = manage_meeting(ctx, "T1", "Schedule", M)
    assert r.message == "Meeting successfully Scheduled" and r.data == {"meeting_id": "NEW-ID"}
    assert db.events == ["begin", "commit"] and ctx.sent == [("S1", "Meeting Scheduled", "NEW-ID")]
    overlap = [c for c in db.calls if "SELECT meeting_id" in c[1]][0]
    assert overlap[2] == ["T1", "2026-11-02", "Cancelled", "11:00", "10:00"]               # (existing_start < new_end) AND (existing_end > new_start)
    insert = [c for c in db.calls if "INSERT INTO D5_MEETINGS" in c[1]][0][2]
    assert insert[4:8] == ["2026-11-02", "10:00", "11:00", "Scheduled"] and insert[3] == "S1"


@pytest.mark.parametrize("owner", [None, "T2"])
def test_uc17_schedule_requires_ownership(owner):
    r = manage_meeting(make_ctx(mm_db(owner=owner)), "T1", "Schedule", M)
    assert r.message == "Security Error: Cannot schedule meeting for an unassigned or invalid query"


def test_uc17_schedule_conflict_and_failures():
    r = manage_meeting(make_ctx(mm_db(conflict=[{"meeting_id": "X"}])), "T1", "Schedule", M)
    assert r.message == "Concurrency Error: Time slot has already been booked (Race Condition Prevented)" and r.http_status == 409
    for failing in ("SELECT assigned_tic, student_id FROM D3_QUERIES", "SELECT meeting_id FROM D5_MEETINGS", "INSERT INTO D5_MEETINGS", "INSERT INTO D7_AUDIT_LOGS"):
        db = put_first(mm_db(), failing, DB_ERR)
        assert manage_meeting(make_ctx(db), "T1", "Schedule", M).message == "Database Error: Failed to schedule meeting safely" and db.events[-1:] in (["rollback"], [])
    db = put_first(mm_db(), "INSERT INTO D5_MEETINGS", DB_ERR)
    manage_meeting(make_ctx(db), "T1", "Schedule", M)
    assert db.events == ["begin", "rollback"]
    assert manage_meeting(make_ctx(mm_db(), dispatch_raises=True), "T1", "Schedule", M).is_success


def test_uc17_cancel():
    mt = [{"assigned_tic": "T1", "student_id": "S1", "status": "Scheduled"}]
    db = mm_db(meeting=mt)
    ctx = make_ctx(db)
    r = manage_meeting(ctx, "T1", "Cancel", {"meeting_id": "M1"})
    assert r.message == "Meeting successfully Cancelled" and r.data == {"meeting_id": "M1"}
    assert ctx.sent == [("S1", "Meeting Cancelled", "M1")] and db.events == ["begin", "commit"]
    assert manage_meeting(make_ctx(mm_db(meeting=[])), "T1", "Cancel", {"meeting_id": "M1"}).message == "Database Error: Meeting reference not found"
    assert manage_meeting(make_ctx(mm_db(meeting=[{"assigned_tic": "T2", "student_id": "S1", "status": "Scheduled"}])), "T1", "Cancel", {"meeting_id": "M1"}).message == "Security Error: Unauthorized attempt to cancel another TIC's meeting"
    r = manage_meeting(make_ctx(mm_db(meeting=[{"assigned_tic": "T1", "student_id": "S1", "status": "Cancelled"}])), "T1", "Cancel", {"meeting_id": "M1"})
    assert r.message == "State Error: Meeting is already cancelled" and r.http_status == 409
    for failing in ("SELECT assigned_tic, student_id, status FROM D5_MEETINGS", "UPDATE D5_MEETINGS", "INSERT INTO D7_AUDIT_LOGS"):
        db = put_first(mm_db(meeting=mt), failing, DB_ERR)
        assert manage_meeting(make_ctx(db), "T1", "Cancel", {"meeting_id": "M1"}).message == "Database Error: Failed to cancel meeting safely"
    assert manage_meeting(make_ctx(mm_db(meeting=mt), dispatch_raises=True), "T1", "Cancel", {"meeting_id": "M1"}).is_success
