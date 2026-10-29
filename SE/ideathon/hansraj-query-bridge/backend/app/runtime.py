"""Glue between the use-case procedures and the real world: builds the per-request Ctx,
implements the "Async" in DispatchNotificationAsync (worker thread + in-app records), and the
pgvector similarity search used by UC-02 in production."""
from __future__ import annotations

import logging
import os
import threading

from .core import Ctx, DatabaseException, new_id, now_iso
from .usecases.notify import dispatch_notification

log = logging.getLogger("hqb")

# UC-06 raises "Meeting Slot Requested"/"Meeting Accepted", which UC-07's event whitelist does not
# contain. The whitelist is kept exactly as documented; these aliases map the two slot events onto
# the documented "Meeting Scheduled" email while the in-app text stays specific.
EVENT_ALIAS = {"Meeting Slot Requested": "Meeting Scheduled", "Meeting Accepted": "Meeting Scheduled"}

IN_APP_TEXT = {
    "New Query Escalated": "A new student query needs review.",
    "Query Assigned": "A query has been assigned to you.",
    "Query Resolved": "Your query has been resolved. Open it to read the resolution.",
    "Document Required": "A document has been requested for your query.",
    "Document Uploaded": "A student uploaded a document for review.",
    "Document Accepted": "Your document was verified.",
    "Document Rejected": "Your document was rejected. Please read the reviewer's note and upload again.",
    "Meeting Scheduled": "A meeting has been scheduled.",
    "Meeting Cancelled": "A meeting has been cancelled.",
    "Meeting Slot Requested": "A student requested one of your meeting slots.",
    "Meeting Accepted": "Your meeting request was accepted.",
}
REF_COLUMN = {"Document Uploaded": "related_document_id", "Meeting Scheduled": "related_meeting_id",
              "Meeting Cancelled": "related_meeting_id", "Meeting Slot Requested": "related_meeting_id",
              "Meeting Accepted": "related_meeting_id"}


def log_error(err) -> None:
    log.warning("%s", err)


def _recipient_ids(db, target: str) -> list[str]:
    if target == "Staff":
        rows = db.query("SELECT U.user_id FROM USERS U JOIN ROLE R ON U.role_id = R.role_id "
                        "WHERE R.role_name IN ('Admin', 'TIC')")
    elif target in ("Admin", "TIC"):
        rows = db.query("SELECT U.user_id FROM USERS U JOIN ROLE R ON U.role_id = R.role_id "
                        "WHERE R.role_name = ?", [target])
    else:
        rows = db.query("SELECT user_id FROM USERS WHERE user_id = ?", [target])
    return [r["user_id"] for r in rows]


def _deliver(database, gw, target, event_type, reference_id) -> None:
    """Runs on a worker thread: record in-app notifications first (so they exist even if email
    fails, SRS 3.5), then run the UC-07 procedure and stamp the email outcome."""
    try:
        with database.session() as db:
            ids = []
            try:
                col = REF_COLUMN.get(event_type, "related_query_id")
                for uid in _recipient_ids(db, target):
                    nid = new_id()
                    db.insert(
                        f"INSERT INTO NOTIFICATIONS (notification_id, recipient_id, {col}, event_type, message, "
                        "delivery_channel, delivery_status) VALUES (?, ?, ?, ?, ?, 'In-App', 'Sent')",
                        [nid, uid, reference_id, event_type, IN_APP_TEXT.get(event_type, event_type)])
                    ids.append(nid)
            except DatabaseException as exc:
                log_error(exc)
            ctx = Ctx(db=db, gw=gw, log_error=log_error)
            result = dispatch_notification(ctx, target, EVENT_ALIAS.get(event_type, event_type), reference_id)
            status = "Sent" if result.is_success else "Failed"
            for nid in ids:
                try:
                    db.update("UPDATE NOTIFICATIONS SET email_status = ? WHERE notification_id = ?", [status, nid])
                except DatabaseException:
                    pass
            if result.is_error:
                log_error(f"Notification email not delivered ({event_type}): {result.message}")
    except Exception as exc:  # noqa: BLE001 - background thread must never crash the process
        log_error(f"Notification worker failed: {exc}")


def make_dispatcher(database, gw):
    def dispatch(target, event_type, reference_id):
        threading.Thread(target=_deliver, args=(database, gw, target, event_type, reference_id),
                         daemon=True).start()
    return dispatch


def pg_vector_search(db, embedding, k):
    """Top-K active KB entries by cosine similarity (1 - cosine distance), computed in PostgreSQL."""
    return db.query(
        "SELECT kb_id, title, content, source, 1 - (embedding <=> ?::vector) AS similarity FROM D2_KNOWLEDGE "
        "WHERE validity_status = 'Active' AND embedding IS NOT NULL "
        "AND (valid_until IS NULL OR valid_until >= CURRENT_DATE) ORDER BY embedding <=> ?::vector LIMIT ?",
        [embedding, embedding, k])


def build_ctx(db, gw, dispatch) -> Ctx:
    mode = os.getenv("RAG_MODE", "pgvector").lower()
    return Ctx(db=db, gw=gw, log_error=log_error, dispatch=dispatch, now=now_iso, new_id=new_id,
               vector_search=(lambda emb, k: pg_vector_search(db, emb, k)) if mode == "pgvector" else None)
