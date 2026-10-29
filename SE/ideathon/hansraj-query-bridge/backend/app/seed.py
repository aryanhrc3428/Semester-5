"""Demo data + setup commands.

    python -m app.seed            create database/schema and seed demo data (idempotent)
    python -m app.seed --reembed  regenerate every KB embedding (after changing embedder/model)

All people, e-mail addresses and KB passages below are SAMPLE data for demonstration. Replace
the KB with verified college information before real use (SRS 3.4: only verified content)."""
from __future__ import annotations

import logging
import os
import sys
import uuid

import psycopg
from psycopg.rows import dict_row

from .config import settings
from .core import NetworkException
from .db import apply_schema, ensure_database
from .gateways import LocalEmbedder, GeminiEmbedder, hash_password

log = logging.getLogger("hqb.seed")
NS = uuid.UUID("6b1c3e0e-5a41-4a52-9b53-0e7a1b0c9d11")
DEMO_PASSWORD = "Hansraj@123"


def uid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


def email_for(local: str) -> str:
    """DEMO_EMAIL=you@gmail.com routes every demo user to your inbox via plus-addressing, which
    lets you see real Resend emails on the free tier (it only delivers to the account owner)."""
    demo = os.getenv("DEMO_EMAIL", "").strip()
    if demo and "@" in demo:
        name, domain = demo.split("@", 1)
        return f"{name}+{local}@{domain}"
    return f"{local}@hansraj.example.edu"


DEPARTMENTS = [("CS", "Computer Science", "Dr. R. Sharma"), ("MATH", "Mathematics", "Dr. A. Verma"),
               ("PHY", "Physics", "Dr. S. Iyer"), ("COM", "Commerce", "Dr. P. Gupta"),
               ("ADM", "College Office", "Registrar")]

USERS = [  # username, role, name, dept code, extra
    ("admin.office", "Admin", "Meera Kapoor (College Office)", "ADM", {}),
    ("tic.cs", "TIC", "Dr. Nikhil Bansal", "CS", {"kb": True}),
    ("tic.math", "TIC", "Dr. Anita Rao", "MATH", {}),
    ("tic.phy", "TIC", "Dr. Suresh Menon", "PHY", {}),
    ("tic.com", "TIC", "Dr. Pooja Malhotra", "COM", {}),
    ("student.aarav", "Student", "Aarav Mehta", "CS", {"year": "Second Year", "cid": "CS2024-014"}),
    ("student.diya", "Student", "Diya Nair", "MATH", {"year": "First Year", "cid": "MA2025-031"}),
    ("student.kabir", "Student", "Kabir Singh", "COM", {"year": "Third Year", "cid": "CO2023-007"}),
]

KB = [
    ("How do I get a bonafide certificate?", "Administrative",
     "To get a bonafide certificate, submit the bonafide request form at the College Office along with your "
     "college ID card. The certificate is normally ready within 2 to 3 working days and can be collected in person."),
    ("What should I do if I lose my college ID card?", "Administrative",
     "If your college ID card is lost, file a written application at the College Office stating the loss and "
     "pay the duplicate-card fee. A duplicate ID card is issued after verification of your enrolment details."),
    ("How can I apply for a No Objection Certificate (NOC) for an internship?", "Administrative",
     "For an internship NOC, submit the offer letter and the NOC request form to your department's "
     "Teacher-in-Charge. After approval it is forwarded to the College Office for the signed certificate."),
    ("Where can I see my examination admit card and exam schedule?", "Academic",
     "Admit cards and the examination schedule are published on the college notice board and the student "
     "portal before the examinations begin. Contact your department TIC if your name is missing from the list."),
    ("How do I apply for re-evaluation of an answer sheet?", "Academic",
     "To apply for re-evaluation, fill the re-evaluation form and pay the prescribed fee within the notified "
     "window after the result is declared. Submit it at the examination branch with a copy of your marksheet."),
    ("What are the attendance requirements?", "Academic",
     "Students are expected to maintain the minimum attendance prescribed by the university. Shortage of "
     "attendance must be reported to the department TIC, who can guide you on condonation procedures."),
    ("How do I pay the semester fee and get a fee receipt?", "Financial",
     "Semester fees are paid through the mode announced by the accounts office. After payment, collect the fee "
     "receipt from the accounts office counter or download it from the payment portal and keep it safe."),
    ("How do I apply for a scholarship?", "Financial",
     "Scholarship applications are accepted when the scholarship cell announces the cycle. Submit the "
     "application form with income, marksheet and identity documents to the scholarship cell by the deadline."),
    ("How can I reset my student portal password?", "Technical",
     "If you cannot log in to the student portal, use the forgot-password option on the login page. If the "
     "problem continues, report it to the computer centre with your college ID number."),
    ("What are the library timings and how do I borrow books?", "Administrative",
     "The library issues books against your college ID card. Check the notice at the library entrance for the "
     "current opening hours, borrowing limit and the fine for late returns."),
]
KB_SOURCE = "Sample data (replace with verified college information)"


def _embedder():
    if settings.uses_gemini:
        return GeminiEmbedder(settings)
    return LocalEmbedder(settings.embed_dim)


def _vec(v) -> str:
    return "[" + ",".join(repr(float(x)) for x in v) + "]"


def seed() -> None:
    ensure_database(settings.database_url)
    apply_schema(settings.database_url)
    emb = _embedder()
    with psycopg.connect(settings.database_url, autocommit=True, row_factory=dict_row) as c:
        if c.execute("SELECT 1 FROM ROLE LIMIT 1").fetchone():
            log.info("Database already seeded; skipping.")
            return
        for r, d in [("Student", "Raises queries, uploads documents, books meetings"),
                     ("Admin", "Triages, resolves and forwards queries; manages the knowledge base"),
                     ("TIC", "Teacher-in-Charge: handles assigned queries, documents and meetings")]:
            c.execute("INSERT INTO ROLE (role_name, description) VALUES (%s, %s)", [r, d])
        role_id = {r["role_name"]: r["role_id"] for r in c.execute("SELECT role_id, role_name FROM ROLE")}
        for code, name, hod in DEPARTMENTS:
            c.execute("INSERT INTO DEPARTMENTS (dept_id, department_name, department_code, hod_name) "
                      "VALUES (%s, %s, %s, %s)", [uid("dept:" + code), name, code, hod])
        pw = hash_password(DEMO_PASSWORD)
        for username, role, name, dept, extra in USERS:
            c.execute(
                "INSERT INTO USERS (user_id, role_id, department_id, user_identity, name, email, college_id_number, "
                "academic_year, kb_permission) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [uid("user:" + username), role_id[role], uid("dept:" + dept), "ident-" + username, name,
                 email_for(username.replace(".", "-")), extra.get("cid"), extra.get("year"), extra.get("kb", False)])
            c.execute("INSERT INTO COLLEGE_DIRECTORY (username, password_hash, user_identity) VALUES (%s,%s,%s)",
                      [username, pw, "ident-" + username])
            if role == "TIC":                       # mock timetable: Mon-Fri free periods
                for wd in range(1, 6):
                    for s, e in [("10:00", "11:00"), ("11:00", "12:00"), ("14:00", "15:00"), ("15:00", "16:00")]:
                        c.execute("INSERT INTO TIMETABLE_PERIODS (tic_id, weekday, start_time, end_time) "
                                  "VALUES (%s,%s,%s,%s)", [uid("user:" + username), wd, s, e])
        admin = uid("user:admin.office")
        for title, cat, content in KB:
            try:
                v = emb.generate_embedding(content, "RETRIEVAL_DOCUMENT")
            except NetworkException as exc:
                log.warning("Embedding failed for seed entry (run --reembed later): %s", exc)
                v = None
            c.execute(
                "INSERT INTO D2_KNOWLEDGE (kb_id, title, content, category, source, verification_status, "
                "validity_status, embedding, created_by, verified_by) VALUES (%s,%s,%s,%s,%s,'Verified','Active',"
                "%s::vector,%s,%s)", [str(uuid.uuid4()), title, content, cat, KB_SOURCE,
                                      _vec(v) if v else None, admin, admin])
        # three demo queries in different workflow states
        aarav, diya, kabir = (uid("user:student." + n) for n in ("aarav", "diya", "kabir"))
        tic_cs, tic_com = uid("user:tic.cs"), uid("user:tic.com")
        rows = [
            (aarav, "CS", "Academic", "Open", None, None,
             "My internal marks for the data structures practical are missing from the portal. Who can correct this?"),
            (aarav, "CS", "Administrative", "Documents Required", tic_cs, "Please upload a scan of your fee receipt.",
             "I need a letter confirming my enrolment for an education loan application."),
            (kabir, "COM", "Financial", "Assigned to TIC", tic_com, None,
             "My scholarship amount was not credited even though I submitted all documents on time."),
        ]
        for stu, dept, cat, status, tic, note, text in rows:
            c.execute(
                "INSERT INTO D3_QUERIES (query_id, student_id, department_id, description, category, status, "
                "source, assigned_tic, doc_request_note) VALUES (%s,%s,%s,%s,%s,%s,'Direct Raise',%s,%s)",
                [str(uuid.uuid4()), stu, uid("dept:" + dept), text, cat, status, tic, note])
    log.info("Seeded demo data. Demo password for every account: %s", DEMO_PASSWORD)


def reembed() -> None:
    emb = _embedder()
    with psycopg.connect(settings.database_url, autocommit=True, row_factory=dict_row) as c:
        rows = c.execute("SELECT kb_id, content FROM D2_KNOWLEDGE").fetchall()
        for r in rows:
            c.execute("UPDATE D2_KNOWLEDGE SET embedding = %s::vector WHERE kb_id = %s",
                      [_vec(emb.generate_embedding(r["content"], "RETRIEVAL_DOCUMENT")), r["kb_id"]])
        print(f"Re-embedded {len(rows)} knowledge-base entries with "
              f"{'Gemini' if settings.uses_gemini else 'the local embedder'}.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if "--reembed" in sys.argv:
        reembed()
    else:
        seed()
