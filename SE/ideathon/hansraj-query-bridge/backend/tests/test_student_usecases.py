"""UC-03 RaiseNewQuery, UC-04 LoadStudentDashboard, UC-05 UploadDocument, UC-06 slots/meetings."""
import io
import pytest
from types import SimpleNamespace as NS

from app.core import DatabaseException
from app.usecases.student import (load_student_dashboard, raise_new_query, upload_document,
                                  view_request_slot_and_accept_meeting as slots)
from .helpers import DB_ERR, NET_ERR, FakeDb, Seq, make_ctx, role

TEXT = "My internal marks are missing from the portal"


# ======================================================================= UC-03
def uc3_db():
    return FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM DEPARTMENTS", [{"dept_id": "D1"}])


@pytest.mark.parametrize("args,expected", [
    ((None, TEXT, "D1", "Academic"), "Validation Failed: Inputs cannot be null"),
    (("S1", None, "D1", "Academic"), "Validation Failed: Inputs cannot be null"),
    (("S1", TEXT, None, "Academic"), "Validation Failed: Inputs cannot be null"),
    (("S1", TEXT, "D1", None), "Validation Failed: Inputs cannot be null"),
    (("S1", 12345678901, "D1", "Academic"), "Validation Failed: Invalid data types"),
    (("S1", TEXT, "D1", 7), "Validation Failed: Invalid data types"),
    (("S1", "too short", "D1", "Academic"), "Validation Failed: Query text length out of bounds"),
    (("S1", "x" * 2001, "D1", "Academic"), "Validation Failed: Query text length out of bounds"),
    (("S1", TEXT, "D1", "Sports"), "Validation Failed: Unrecognized query category"),
])
def test_uc3_validation(args, expected):
    r = raise_new_query(make_ctx(uc3_db()), *args)
    assert r.message == expected and r.http_status == 400


@pytest.mark.parametrize("category", ["Academic", "Administrative", "Technical", "Financial"])
@pytest.mark.parametrize("n", [10, 2000])
def test_uc3_success_for_every_category_and_boundary(category, n):
    db = uc3_db()
    ctx = make_ctx(db)
    r = raise_new_query(ctx, "S1", "x" * n, "D1", category)
    assert r.is_success and r.message == "Query submitted successfully" and r.data == {"query_id": "NEW-ID"}
    assert db.events == ["begin", "commit"]
    insert = [c for c in db.calls if "INSERT INTO D3_QUERIES" in c[1]][0]
    assert insert[2][5] == "Open" and insert[2][0] == "NEW-ID"             # initial status per pseudocode
    assert any("D7_AUDIT_LOGS" in c[1] for c in db.calls)
    assert ctx.sent == [("Admin", "New Query Escalated", "NEW-ID")]


def test_uc3_unknown_student_and_department():
    assert raise_new_query(make_ctx(FakeDb().on("FROM USERS", [])), "S1", TEXT, "D1", "Academic").message \
        == "Database Error: Invalid student identity"
    db = FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM DEPARTMENTS", [])
    assert raise_new_query(make_ctx(db), "S1", TEXT, "D9", "Academic").message == "Database Error: Invalid department reference"


def test_uc3_relational_check_exception():
    r = raise_new_query(make_ctx(FakeDb().on("FROM USERS", DB_ERR)), "S1", TEXT, "D1", "Academic")
    assert r.message == "System Error: Unable to validate relational constraints"


@pytest.mark.parametrize("failing", ["INSERT INTO D3_QUERIES", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc3_transaction_rolls_back_and_skips_notification(failing):
    db = uc3_db().on(failing, DB_ERR)
    ctx = make_ctx(db)
    r = raise_new_query(ctx, "S1", TEXT, "D1", "Academic")
    assert r.message == "Database Error: Failed to save new query"
    assert db.events == ["begin", "rollback"] and ctx.sent == []


def test_uc3_notification_failure_is_non_blocking():
    ctx = make_ctx(uc3_db(), dispatch_raises=True)
    r = raise_new_query(ctx, "S1", TEXT, "D1", "Academic")
    assert r.is_success and any("Failed to dispatch notification for query NEW-ID" in l for l in ctx.logs)


# ======================================================================= UC-04
@pytest.mark.parametrize("sid,expected", [(None, "Validation Failed: Student ID cannot be null"),
                                          (42, "Validation Failed: Invalid data type for Student ID")])
def test_uc4_validation(sid, expected):
    assert load_student_dashboard(make_ctx(), sid).message == expected


def test_uc4_user_checks():
    assert load_student_dashboard(make_ctx(FakeDb().on("FROM USERS", [])), "S1").message == "Database Error: Student identity not found"
    assert load_student_dashboard(make_ctx(FakeDb().on("FROM USERS", DB_ERR)), "S1").message == "System Error: Unable to validate user identity"


def test_uc4_query_retrieval_failure_and_empty():
    db = FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM D3_QUERIES", DB_ERR)
    assert load_student_dashboard(make_ctx(db), "S1").message == "Database Error: Failed to retrieve student queries"
    db = FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM D3_QUERIES", [])
    r = load_student_dashboard(make_ctx(db), "S1")
    assert r.is_success and r.message == "No queries found" and r.data == []


def test_uc4_aggregates_documents_and_meetings_in_order():
    qs = [{"query_id": "Q2"}, {"query_id": "Q1"}]
    db = (FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM D3_QUERIES", qs)
          .on("FROM D4_DOCUMENTS", lambda p: [{"document_id": "doc-" + p[0]}])
          .on("FROM D5_MEETINGS", lambda p: [{"meeting_id": "m-" + p[0]}]))
    r = load_student_dashboard(make_ctx(db), "S1")
    assert r.message == "Dashboard data retrieved successfully"
    assert [x["query_details"]["query_id"] for x in r.data] == ["Q2", "Q1"]
    assert r.data[0]["documents"] == [{"document_id": "doc-Q2"}] and r.data[1]["meetings"] == [{"meeting_id": "m-Q1"}]


@pytest.mark.parametrize("failing", ["FROM D4_DOCUMENTS", "FROM D5_MEETINGS"])
def test_uc4_corrupt_relation_degrades_gracefully(failing):
    db = (FakeDb().on("FROM USERS", [{"user_id": "S1"}]).on("FROM D3_QUERIES", [{"query_id": "Q1"}, {"query_id": "Q2"}])
          .on(failing, Seq(DB_ERR, [])))
    ctx = make_ctx(db)
    r = load_student_dashboard(ctx, "S1")
    assert r.is_success and r.data[0]["documents"] == "Data unavailable" and r.data[0]["meetings"] == "Data unavailable"
    assert r.data[1]["documents"] != "Data unavailable" and ctx.logs


# ======================================================================= UC-05
def f(name="proof.pdf", size=1000):
    return NS(name=name, size=size, stream=io.BytesIO(b"x"))


class Store:
    def __init__(self, key="queries/Q1/abc-proof.pdf", exc=None):
        self.key, self.exc, self.deleted = key, exc, []

    def upload_stream(self, stream, name, qid):
        if self.exc:
            raise self.exc
        return self.key

    def delete(self, key):
        self.deleted.append(key)


def uc5_db(owner="S1"):
    return FakeDb().on("FROM D3_QUERIES", [{"student_id": owner, "status": "Documents Required"}])


@pytest.mark.parametrize("args,expected", [
    ((None, "Q1", f()), "Validation Failed: Inputs cannot be null"),
    (("S1", None, f()), "Validation Failed: Inputs cannot be null"),
    (("S1", "Q1", None), "Validation Failed: Inputs cannot be null"),
    (("S1", "Q1", NS(name=5, size=10)), "Validation Failed: Invalid file object structure"),
    (("S1", "Q1", NS(name="a.pdf", size="10")), "Validation Failed: Invalid file object structure"),
    (("S1", "Q1", f(size=0)), "Validation Failed: File size must be between 1 byte and 25MB"),
    (("S1", "Q1", f(size=25 * 1024 * 1024 + 1)), "Validation Failed: File size must be between 1 byte and 25MB"),
    (("S1", "Q1", f("virus.exe")), "Validation Failed: Unsupported file format detected"),
    (("S1", "Q1", f("noextension")), "Validation Failed: Unsupported file format detected"),
])
def test_uc5_validation(args, expected):
    store = Store()
    r = upload_document(make_ctx(uc5_db(), storage=store), *args)
    assert r.message == expected and r.http_status == 400


@pytest.mark.parametrize("name,ext", [("a.pdf", "PDF"), ("a.JPG", "JPG"), ("a.jpeg", "JPEG"), ("a.PnG", "PNG"), ("my.scan.pdf", "PDF")])
def test_uc5_success_and_size_boundary(name, ext):
    db = uc5_db()
    ctx = make_ctx(db, storage=Store())
    r = upload_document(ctx, "S1", "Q1", f(name, 25 * 1024 * 1024))
    assert r.is_success and r.message == "Document securely uploaded and linked" and r.data == {"document_id": "NEW-ID"}
    ins = [c for c in db.calls if "INSERT INTO D4_DOCUMENTS" in c[1]][0][2]
    assert ins[4] == ext and ins[7] == "Pending Review"
    assert [c for c in db.calls if "UPDATE D3_QUERIES" in c[1]][0][2][0] == "Document Submitted"
    assert db.events == ["begin", "commit"] and ctx.sent == [("Staff", "Document Uploaded", "NEW-ID")]


def test_uc5_ownership_and_reference_checks():
    assert upload_document(make_ctx(FakeDb().on("FROM D3_QUERIES", []), storage=Store()), "S1", "Q9", f()).message == "Database Error: Invalid query reference"
    r = upload_document(make_ctx(uc5_db(owner="S2"), storage=Store()), "S1", "Q1", f())
    assert r.message == "Security Error: Unauthorized attempt to upload to another user's query" and r.http_status == 403
    assert upload_document(make_ctx(FakeDb().on("FROM D3_QUERIES", DB_ERR), storage=Store()), "S1", "Q1", f()).message == "System Error: Unable to validate query ownership"


def test_uc5_storage_failures():
    r = upload_document(make_ctx(uc5_db(), storage=Store(key=None)), "S1", "Q1", f())
    assert r.message == "Cloud Error: S3 returned null storage key" and r.http_status == 503
    ctx = make_ctx(uc5_db(), storage=Store(exc=NET_ERR))
    assert upload_document(ctx, "S1", "Q1", f()).message == "System Error: File upload service temporarily unavailable" and ctx.logs


def test_uc5_db_failure_rolls_back_and_cleans_storage():
    store = Store()
    db = uc5_db().on("INSERT INTO D4_DOCUMENTS", DB_ERR)
    r = upload_document(make_ctx(db, storage=store), "S1", "Q1", f())
    assert r.message == "Database Error: Failed to save document records"
    assert db.events == ["begin", "rollback"] and store.deleted == ["queries/Q1/abc-proof.pdf"]


def test_uc5_cleanup_error_does_not_mask_failure():
    class BadStore(Store):
        def delete(self, key):
            raise RuntimeError("cleanup failed")
    db = uc5_db().on("UPDATE D3_QUERIES", DB_ERR)
    assert upload_document(make_ctx(db, storage=BadStore()), "S1", "Q1", f()).message == "Database Error: Failed to save document records"


def test_uc5_notification_failure_is_non_blocking():
    ctx = make_ctx(uc5_db(), storage=Store(), dispatch_raises=True)
    assert upload_document(ctx, "S1", "Q1", f()).is_success


# ======================================================================= UC-06
@pytest.mark.parametrize("args,expected", [
    ((None, "ViewSlots", {}), "Validation Failed: Core parameters cannot be null"),
    (("S1", None, {}), "Validation Failed: Core parameters cannot be null"),
    (("S1", "ViewSlots", None), "Validation Failed: Core parameters cannot be null"),
    ((7, "ViewSlots", {}), "Validation Failed: Invalid parameter data types"),
    (("S1", 7, {}), "Validation Failed: Invalid parameter data types"),
    (("S1", "ViewSlots", "x"), "Validation Failed: Invalid parameter data types"),
    (("S1", "DeleteSlot", {}), "Validation Failed: Action must be 'ViewSlots', 'RequestSlot', or 'AcceptMeeting'"),
])
def test_uc6_validation(args, expected):
    assert slots(make_ctx(FakeDb().on("ROLE", role("Student"))), *args).message == expected


def test_uc6_rbac_lookup_failures():
    assert slots(make_ctx(FakeDb().on("ROLE", [])), "S1", "ViewSlots", {}).message == "Security Error: User account not found"
    assert slots(make_ctx(FakeDb().on("ROLE", DB_ERR)), "S1", "ViewSlots", {}).message == "System Error: Unable to validate permissions"


def test_uc6_view_slots():
    db = FakeDb().on("ROLE", role("Student")).on("D6_TIME_SLOTS", [{"slot_id": "SL1"}])
    r = slots(make_ctx(db), "S1", "ViewSlots", {"tic_id": "T1", "target_date": "2026-11-02"})
    assert r.message == "Available slots retrieved successfully" and r.data == [{"slot_id": "SL1"}]
    assert db.calls[-1][2] == ["T1", "2026-11-02", "Available"]
    for bad in ({"tic_id": "T1"}, {"target_date": "2026-11-02"}):
        assert slots(make_ctx(db), "S1", "ViewSlots", bad).message == "Validation Failed: TIC ID and target date required to view slots"
    db2 = FakeDb().on("ROLE", role("Student")).on("D6_TIME_SLOTS", DB_ERR)
    assert slots(make_ctx(db2), "S1", "ViewSlots", {"tic_id": "T1", "target_date": "d"}).message == "Database Error: Failed to retrieve slot availability"


def req_db(slot=None, role_name="Student"):
    return FakeDb().on("ROLE", role(role_name)).on("SELECT assigned_tic, status FROM D6", slot if slot is not None else [{"assigned_tic": "T1", "status": "Available"}])


def test_uc6_request_slot_success():
    db = req_db()
    ctx = make_ctx(db)
    r = slots(ctx, "S1", "RequestSlot", {"slot_id": "SL1", "query_id": "Q1"})
    assert r.message == "Action successfully processed: RequestSlot" and r.data == {"reference_id": "SL1"}
    assert db.events == ["begin", "commit"] and ctx.sent == [("T1", "Meeting Slot Requested", "SL1")]
    assert [c for c in db.calls if "UPDATE D6_TIME_SLOTS" in c[1]][0][2][:2] == ["Requested", "S1"]


@pytest.mark.parametrize("role_name,data,expected", [
    ("TIC", {"slot_id": "SL1", "query_id": "Q1"}, "Security Error: Only students can request meeting slots"),
    ("Student", {"query_id": "Q1"}, "Validation Failed: Slot ID and Query ID required for request"),
    ("Student", {"slot_id": "SL1"}, "Validation Failed: Slot ID and Query ID required for request"),
])
def test_uc6_request_slot_guards(role_name, data, expected):
    assert slots(make_ctx(req_db(role_name=role_name)), "S1", "RequestSlot", data).message == expected


@pytest.mark.parametrize("slot", [[], [{"assigned_tic": "T1", "status": "Requested"}]])
def test_uc6_request_unavailable_slot(slot):
    r = slots(make_ctx(req_db(slot)), "S1", "RequestSlot", {"slot_id": "SL1", "query_id": "Q1"})
    assert r.message == "State Error: Selected slot is no longer available" and r.http_status == 409


@pytest.mark.parametrize("failing", ["SELECT assigned_tic, status FROM D6", "UPDATE D6_TIME_SLOTS", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc6_request_database_failures_roll_back(failing):
    db = FakeDb().on("ROLE", role("Student")).on(failing, DB_ERR).on("SELECT assigned_tic, status FROM D6", [{"assigned_tic": "T1", "status": "Available"}])
    r = slots(make_ctx(db), "S1", "RequestSlot", {"slot_id": "SL1", "query_id": "Q1"})
    assert r.message == "Database Error: Failed to process slot request securely" and db.events[-1] == "rollback"


def acc_db(slot, role_name="TIC"):
    return FakeDb().on("ROLE", role(role_name)).on("SELECT assigned_tic, student_id, status FROM D6", slot)


def test_uc6_accept_success():
    db = acc_db([{"assigned_tic": "T1", "student_id": "S1", "status": "Requested"}])
    ctx = make_ctx(db)
    r = slots(ctx, "T1", "AcceptMeeting", {"slot_id": "SL1"})
    assert r.message == "Action successfully processed: AcceptMeeting" and ctx.sent == [("S1", "Meeting Accepted", "SL1")]
    assert db.events == ["begin", "commit"]


@pytest.mark.parametrize("role_name,data,slot,expected", [
    ("Student", {"slot_id": "SL1"}, [], "Security Error: Only TICs can accept meeting slots"),
    ("TIC", {}, [], "Validation Failed: Slot ID required to accept meeting"),
    ("TIC", {"slot_id": "SL1"}, [], "Database Error: Slot reference not found"),
    ("TIC", {"slot_id": "SL1"}, [{"assigned_tic": "T2", "student_id": "S1", "status": "Requested"}], "Security Error: Unauthorized attempt to accept another TIC's slot"),
    ("TIC", {"slot_id": "SL1"}, [{"assigned_tic": "T1", "student_id": None, "status": "Available"}], "State Error: Slot must be in 'Requested' state to accept"),
])
def test_uc6_accept_guards(role_name, data, slot, expected):
    assert slots(make_ctx(acc_db(slot, role_name)), "T1", "AcceptMeeting", data).message == expected


@pytest.mark.parametrize("failing", ["SELECT assigned_tic, student_id, status FROM D6", "UPDATE D6_TIME_SLOTS", "INSERT INTO D7_AUDIT_LOGS"])
def test_uc6_accept_database_failures(failing):
    db = FakeDb().on("ROLE", role("TIC")).on(failing, DB_ERR).on("SELECT assigned_tic, student_id, status FROM D6", [{"assigned_tic": "T1", "student_id": "S1", "status": "Requested"}])
    r = slots(make_ctx(db), "T1", "AcceptMeeting", {"slot_id": "SL1"})
    assert r.message == "Database Error: Failed to accept meeting slot safely"


def test_uc6_notification_failure_non_blocking():
    ctx = make_ctx(acc_db([{"assigned_tic": "T1", "student_id": "S1", "status": "Requested"}]), dispatch_raises=True)
    assert slots(ctx, "T1", "AcceptMeeting", {"slot_id": "SL1"}).is_success
    ctx = make_ctx(req_db(), dispatch_raises=True)
    assert slots(ctx, "S1", "RequestSlot", {"slot_id": "SL1", "query_id": "Q1"}).is_success
