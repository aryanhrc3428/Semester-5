import math
import pytest

from app.core import cosine_similarity
from app.usecases.rag import resolve_query_rag
from .helpers import DB_ERR, NET_ERR, FakeDb, make_ctx

Q = "How to apply for leave?"


class Emb:
    def __init__(self, vec=None, exc=None):
        self.vec, self.exc = vec, exc

    def generate_embedding(self, text, task="RETRIEVAL_QUERY"):
        if self.exc:
            raise self.exc
        return self.vec


class Llm:
    def __init__(self, answer="Answer text", exc=None):
        self.answer, self.exc, self.seen = answer, exc, None

    def generate_grounded_response(self, q, ctx):
        self.seen = ctx
        if self.exc:
            raise self.exc
        return self.answer


def entry(i, emb, source="Src"):
    return {"kb_id": f"KB{i}", "content": f"content {i}", "source": source, "embedding": emb}


def run(rows, emb=None, llm=None, threshold=0.5, query=Q):
    db = FakeDb().on("D2_KNOWLEDGE", rows)
    ctx = make_ctx(db, embedder=emb or Emb([1.0, 0.0]), llm=llm or Llm())
    return resolve_query_rag(ctx, query, threshold), ctx


@pytest.mark.parametrize("q,t,expected", [
    (None, 0.5, "Validation Failed: Inputs cannot be null"),
    (Q, None, "Validation Failed: Inputs cannot be null"),
    (40482, 0.5, "Validation Failed: Invalid data types"),
    (Q, 1, "Validation Failed: Invalid data types"),        # int is not a float
    (Q, "0.5", "Validation Failed: Invalid data types"),
    ("Why", 0.5, "Validation Failed: Query length out of bounds"),
    ("x" * 1001, 0.5, "Validation Failed: Query length out of bounds"),
    (Q, -0.01, "Validation Failed: Threshold must be between 0.0 and 1.0"),
    (Q, 1.01, "Validation Failed: Threshold must be between 0.0 and 1.0"),
])
def test_validation(q, t, expected):
    ctx = make_ctx(FakeDb(), embedder=Emb([1.0]), llm=Llm())
    r = resolve_query_rag(ctx, q, t)
    assert r.message == expected and r.http_status == 400 and ctx.db.calls == []


@pytest.mark.parametrize("q,t", [("x" * 5, 0.0), ("x" * 1000, 1.0)])
def test_boundaries_accepted(q, t):
    r, _ = run([entry(1, [1.0, 0.0])], threshold=t, query=q)
    assert r.is_success


@pytest.mark.parametrize("vec", [None, []])
def test_invalid_embedding(vec):
    r, _ = run([], emb=Emb(vec))
    assert r.message == "API Error: Failed to generate valid embedding vector"


def test_embedding_network_failure():
    r, ctx = run([], emb=Emb(exc=NET_ERR))
    assert r.message == "System Error: AI Embedding service unavailable" and ctx.logs


def test_empty_knowledge_base_escalates():
    r, _ = run([])
    assert (r.kind, r.message, r.action, r.reason) == ("response", "Escalation Required", "Raise Query to Admin", "Knowledge Base empty")


def test_database_failure():
    db = FakeDb().on("D2_KNOWLEDGE", DB_ERR)
    r = resolve_query_rag(make_ctx(db, embedder=Emb([1.0]), llm=Llm()), Q, 0.5)
    assert r.message == "Database Error: Failed to retrieve Knowledge Base entries"


def test_invalid_entries_are_skipped_and_escalate():
    rows = [entry(1, None), entry(2, [1.0, 0.0, 0.0]), entry(3, [0.0, 0.0])]    # null / length mismatch / zero vector
    r, _ = run(rows)
    assert (r.kind, r.message, r.action, r.reason) == ("response", "Escalation Required", "Raise Query to Admin", None)


def test_below_threshold_escalates():
    r, _ = run([entry(1, [0.0, 1.0])], threshold=0.5)
    assert r.kind == "response" and r.reason is None


def test_grounded_answer_top_five_sorted_with_sources():
    rows = [entry(i, [math.cos(i / 10), math.sin(i / 10)], source=f"S{i}") for i in (6, 1, 4, 0, 3, 5, 2)]
    llm = Llm("Apply via the college office.")
    r, _ = run(rows, llm=llm, threshold=0.5)
    assert r.is_success and r.message == "Grounded Answer"
    assert r.data["answer"] == "Apply via the college office."
    assert r.data["sources"] == ["S0", "S1", "S2", "S3", "S4"]          # best five, descending
    assert len(llm.seen) == 5 and r.data["confidence"] == pytest.approx(1.0)


@pytest.mark.parametrize("answer", [None, ""])
def test_empty_ai_answer_escalates(answer):
    r, _ = run([entry(1, [1.0, 0.0])], llm=Llm(answer))
    assert (r.message, r.reason) == ("Escalation Required", "AI Generation Failed")


def test_generation_network_failure():
    r, ctx = run([entry(1, [1.0, 0.0])], llm=Llm(exc=NET_ERR))
    assert r.message == "System Error: AI Generation service unavailable" and ctx.logs


# ---- production (pgvector) path --------------------------------------------------------------
def test_vector_search_path():
    ctx = make_ctx(FakeDb(), embedder=Emb([1.0, 0.0]), llm=Llm("A"))
    ctx.vector_search = lambda emb, k: [{"kb_id": "K1", "content": "c", "source": "S", "similarity": 0.9}]
    assert resolve_query_rag(ctx, Q, 0.5).data["sources"] == ["S"]
    ctx.vector_search = lambda emb, k: []
    assert resolve_query_rag(ctx, Q, 0.5).reason == "Knowledge Base empty"
    ctx.vector_search = lambda emb, k: [{"kb_id": "K1", "content": "c", "source": "S", "similarity": 0.2}]
    assert resolve_query_rag(ctx, Q, 0.5).reason is None


def test_vector_search_database_error():
    ctx = make_ctx(FakeDb(), embedder=Emb([1.0]), llm=Llm())

    def boom(emb, k):
        raise DB_ERR
    ctx.vector_search = boom
    assert resolve_query_rag(ctx, Q, 0.5).message == "Database Error: Failed to retrieve Knowledge Base entries"


def test_cosine_similarity_math():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine_similarity([1, 1], [-1, -1]) == pytest.approx(-1.0)
    assert cosine_similarity([0, 0], [1, 1]) is None
