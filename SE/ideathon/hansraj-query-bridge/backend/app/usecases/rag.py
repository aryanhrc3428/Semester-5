"""UC-02 ResolveQueryRAG -- mirrors pseudocode/UC-02.pseudo.

The reference path loads every Active KB entry and computes cosine similarity with explicit
loops (steps 3-4). In production a pgvector search (`ctx.vector_search`) replaces steps 3-4
with the identical cosine measure computed inside PostgreSQL, so the 100k-entry / 8 s
requirement (SRS 3.4.4) holds; steps 1, 2, 5 and 6 are unchanged."""
from ..core import (Ctx, DatabaseException, NetworkException, cosine_similarity, err, is_float, is_str,
                    response, success)

TOP_K = 5


def resolve_query_rag(ctx: Ctx, student_query, threshold_T):
    # 1. Initial Type, Null, and Boundary Validation
    if student_query is None or threshold_T is None:
        return err("Validation Failed: Inputs cannot be null")
    if not is_str(student_query) or not is_float(threshold_T):
        return err("Validation Failed: Invalid data types")
    if len(student_query) < 5 or len(student_query) > 1000:
        return err("Validation Failed: Query length out of bounds")
    if threshold_T < 0.0 or threshold_T > 1.0:
        return err("Validation Failed: Threshold must be between 0.0 and 1.0")
    # 2. Generate Embedding with Network Resilience
    query_embedding = None
    try:
        query_embedding = ctx.gw.embedder.generate_embedding(student_query, "RETRIEVAL_QUERY")
        if query_embedding is None or len(query_embedding) == 0:
            return err("API Error: Failed to generate valid embedding vector")
    except NetworkException as net_err:
        ctx.log_error(net_err)
        return err("System Error: AI Embedding service unavailable")
    # 3. Secure Database Retrieval  /  4. Similarity
    results = []
    if ctx.vector_search is not None:
        try:
            results = [(e, e["similarity"]) for e in ctx.vector_search(query_embedding, TOP_K)]
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to retrieve Knowledge Base entries")
        if not results:
            return response("Escalation Required", "Raise Query to Admin", "Knowledge Base empty")
    else:
        try:
            candidate_entries = ctx.db.query(
                "SELECT kb_id, content, source, embedding FROM D2_KNOWLEDGE WHERE validity_status = ?", ["Active"])
            if not candidate_entries:
                return response("Escalation Required", "Raise Query to Admin", "Knowledge Base empty")
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to retrieve Knowledge Base entries")
        for entry in candidate_entries:
            emb = entry.get("embedding")
            if emb is not None and len(emb) == len(query_embedding):
                similarity_score = cosine_similarity(query_embedding, emb)
                if similarity_score is not None:
                    results.append((entry, similarity_score))
    # 5. Evaluate Threshold and Extract Top K
    results.sort(key=lambda pair: pair[1], reverse=True)
    top_k_context = results[:TOP_K]
    if len(top_k_context) == 0 or results[0][1] < threshold_T:
        return response("Escalation Required", "Raise Query to Admin")
    # 6. Generate Grounded AI Response
    try:
        context = [dict(entry, similarity=score) for entry, score in top_k_context]
        ai_answer = ctx.gw.llm.generate_grounded_response(student_query, context)
        if ai_answer is None or len(ai_answer) == 0:
            return response("Escalation Required", "Raise Query to Admin", "AI Generation Failed")
        sources_list = [entry.get("source") for entry, _ in top_k_context]
        return success("Grounded Answer", {
            "answer": ai_answer, "sources": sources_list,
            "confidence": results[0][1], "kb_ids": [e.get("kb_id") for e, _ in top_k_context]})
    except NetworkException as net_err:
        ctx.log_error(net_err)
        return err("System Error: AI Generation service unavailable")
