# Hansraj Query Bridge

Implementation of the Hansraj Query Bridge SRS, pseudocode (UC-01 to UC-17), DFDs, ER diagram and test
suites. Students get verified answers from an AI assistant (RAG over a verified knowledge base) or send
the query to staff; Admins triage, resolve and forward; Teachers-in-Charge (TICs) handle assigned
queries, request/review documents and manage meetings.

Cost to run: **$0**. Defaults need nothing but PostgreSQL, Python and Node.

```
backend/    FastAPI + PostgreSQL/pgvector. app/usecases/ = one procedure per pseudocode file
frontend/   Next.js 14 (React, TypeScript). Student, Admin and TIC dashboards
docs/       DECISIONS.md: how document inconsistencies were resolved, what is mocked or not covered
```

## 1. Prerequisites
| Need | Version | Notes |
|---|---|---|
| Python | 3.10+ | |
| Node.js | 18.17+ | |
| PostgreSQL + pgvector | 14+ | easiest: `docker compose up -d db` (uses the `pgvector/pgvector:pg16` image) |

No Docker? Install PostgreSQL and pgvector yourself (Ubuntu: `sudo apt install postgresql postgresql-16-pgvector`),
then set `DATABASE_URL` in `backend/.env` (default `postgresql://postgres:postgres@localhost:5432/hansraj_qb`).
The database user must be allowed to create a database and the `vector` and `btree_gist` extensions.

## 2. Run it
Terminal 1: database and API
```bash
docker compose up -d db          # skip if you already run PostgreSQL
./run_backend.sh                 # Windows: run_backend.bat
```
Terminal 2: web app
```bash
./run_frontend.sh                # Windows: run_frontend.bat
```
Open **http://localhost:3000**. On first start the backend creates the database, schema and demo data
automatically (`AUTO_SETUP=true`). API docs: http://127.0.0.1:8000/docs.

Manual equivalent:
```bash
cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m app.seed && uvicorn app.main:app --port 8000      # seed is optional (startup does it)
cd ../frontend && npm install && npm run dev
```

## 3. Demo accounts (password `Hansraj@123`)
| Role | Username | Notes |
|---|---|---|
| Student | `student.aarav`, `student.diya`, `student.kabir` | |
| Admin | `admin.office` | |
| TIC | `tic.cs` (has KB permission), `tic.math`, `tic.phy`, `tic.com` | free periods Mon to Fri: 10-12, 14-16 |

Try this flow: sign in as a student, ask "How do I get a bonafide certificate?", ask something unrelated and
send it to staff; as `admin.office` forward it to a TIC; as the TIC request a document; as the student
upload a PDF/JPG/PNG; as the TIC accept it, publish a meeting slot, resolve the query.

## 4. Optional free services
Create `backend/.env` (copy `backend/.env.example`):
* **Gemini (free tier)**: set `GEMINI_API_KEY` (https://aistudio.google.com/apikey). Then run
  `python -m app.seed --reembed` once so stored knowledge-base vectors match the Gemini embedding space.
  Models are configurable (`GEMINI_EMBED_MODEL`, `GEMINI_CHAT_MODEL`); check Google's current model names and
  free-tier limits. Without a key a local lexical embedder and an extractive answerer are used (offline, works
  for demos, less semantic).
* **Resend (free tier)**: set `RESEND_API_KEY`. The free sandbox sender only delivers to your own account
  address: set `DEMO_EMAIL=you@gmail.com` **before the first run** (or re-seed) so demo users' addresses become
  `you+role@gmail.com`. Without a key emails are written to the backend log; in-app notifications always work.
* **S3**: `STORAGE_BACKEND=s3`, `S3_BUCKET=...`, `pip install boto3` (AWS is not free). Default is local disk.

Deploying beyond a demo: set a strong `JWT_SECRET`, run behind HTTPS, replace the seeded college directory
(`COLLEGE_DIRECTORY`, a stand-in for the college login service) and timetable (`TIMETABLE_PERIODS`) adapters in
`backend/app/gateways.py` with the real services, and replace the sample knowledge base with verified content.

## 5. Tests
```bash
cd backend && pytest -q                 # needs PostgreSQL for test_api_integration.py (auto-skipped if absent)
pytest --cov=app.usecases --cov-branch  # 100% statement / 99% branch coverage of the 17 procedures
```
* `test_uc*` / `test_*_usecases.py`: every branch of every procedure (validation, RBAC/IDOR, exceptions,
  transaction rollback, non-blocking notifications) with scripted fakes.
* `test_traceability.py`: every message expected by the documented test suites TS-UC01..17 exists verbatim in the code.
* `test_api_integration.py`: full workflow through the HTTP API on a real database.

## 6. Layout of the code
`backend/app/usecases/{auth,rag,student,notify,admin,tic}.py` hold UC-01..UC-17 line-for-line with the
pseudocode. `main.py` is the HTTP layer (JWT, RBAC, lockout, rate limit, uploads); `gateways.py` the external
service adapters; `schema.sql` the database; `runtime.py` async notifications and pgvector search.
