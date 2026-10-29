"""Admin-side use cases: UC-08 AdminViewNewQueries, UC-09 AdminResolveQuery,
UC-10 ForwardQueryToTIC, UC-11 KnowledgeBaseManagement. Mirrors the pseudocode files."""
from ..core import (Ctx, DatabaseException, NetworkException, ROLE_SQL, SystemException, err, first, is_bool,
                    is_dict, is_str, success)

# UC-11 treats a TIC holding KB permission as the "Authorized TIC" role (SRS 3.4.3-D).
KB_ROLE_SQL = ("SELECT CASE WHEN R.role_name = 'TIC' AND U.kb_permission THEN 'Authorized TIC' "
               "ELSE R.role_name END AS role_name FROM USERS U JOIN ROLE R ON U.role_id = R.role_id "
               "WHERE U.user_id = ?")


# ===================================================================================== UC-08
def admin_view_new_queries(ctx: Ctx, admin_id):
    # 1. Initial Type and Null Validation
    if admin_id is None:
        return err("Validation Failed: Admin ID cannot be null")
    if not is_str(admin_id):
        return err("Validation Failed: Invalid data type for Admin ID")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [admin_id]))
        if not role_record:
            return err("Database Error: Admin identity not found")
        if role_record["role_name"] != "Admin":
            return err("Security Error: Unauthorized access. Admin privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Secure Base Query Retrieval
    try:
        open_queries = ctx.db.query("SELECT * FROM D3_QUERIES WHERE status = ? ORDER BY created_at ASC", ["Open"])
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("Database Error: Failed to retrieve open queries")
    if len(open_queries) == 0:
        return success("No new queries found", [])
    # 4. Data Aggregation Loop for Dashboard Context
    admin_dashboard_view = []
    for i in range(len(open_queries)):
        current_query = open_queries[i]
        student_details = {}
        try:
            student_record = first(ctx.db.query("SELECT name, email FROM USERS WHERE user_id = ?",
                                                [current_query["student_id"]]))
            if student_record:
                student_details["name"] = student_record["name"]
                student_details["email"] = student_record["email"]
            else:
                student_details["name"] = "Unknown Student"
                student_details["email"] = "Unknown Email"
        except DatabaseException:
            ctx.log_error("Warning: Failed to load student details for query " + current_query["query_id"])
            student_details["name"] = "Data unavailable"
            student_details["email"] = "Data unavailable"
        # 5. Construct Compiled Record
        admin_dashboard_view.insert(i, {"query_details": current_query, "student_info": student_details})
    return success("Admin dashboard data retrieved successfully", admin_dashboard_view)


# ===================================================================================== UC-09
def admin_resolve_query(ctx: Ctx, admin_id, query_id, resolution_text, add_to_kb_flag):
    # 1. Initial Type, Null, and Boundary Validation
    if admin_id is None or query_id is None or resolution_text is None or add_to_kb_flag is None:
        return err("Validation Failed: Parameters cannot be null")
    if (not is_str(admin_id) or not is_str(query_id) or not is_str(resolution_text)
            or not is_bool(add_to_kb_flag)):
        return err("Validation Failed: Invalid parameter data types")
    if len(resolution_text) < 10 or len(resolution_text) > 5000:
        return err("Validation Failed: Resolution text length out of bounds")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [admin_id]))
        if not role_record or role_record["role_name"] != "Admin":
            return err("Security Error: Unauthorized access. Admin privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Relational Integrity: Validate Query Existence
    try:
        target_query = first(ctx.db.query(
            "SELECT student_id, description, category FROM D3_QUERIES WHERE query_id = ?", [query_id]))
        if not target_query:
            return err("Database Error: Target query reference not found")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query reference")
    # 4. Secure Database Transaction for Resolution and Audit
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.update("UPDATE D3_QUERIES SET status = ?, resolution = ?, resolved_by = ?, updated_at = ? "
                      "WHERE query_id = ?", ["Resolved", resolution_text, admin_id, current_time, query_id])
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                      "VALUES (?, ?, ?, ?, ?)", [admin_id, "Resolve", "Query", query_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to resolve query and commit audit log")
    # 5. Conditional Knowledge Base Escalation (isolated from main transaction)
    if add_to_kb_flag is True:
        try:
            kb_payload = {"title": target_query["description"], "content": resolution_text,
                          "category": target_query["category"], "source": "Admin Resolution"}
            kb_result = (ctx.kb_manage or knowledge_base_management)(ctx, admin_id, "Create", kb_payload)
            if getattr(kb_result, "is_error", False):
                ctx.log_error("Warning: Failed to add resolution to Knowledge Base for query " + query_id)
        except SystemException:
            ctx.log_error("Warning: Failed to add resolution to Knowledge Base for query " + query_id)
    # 6. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch(target_query["student_id"], "Query Resolved", query_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch resolution notification to student for query " + query_id)
    return success("Query successfully resolved", {"query_id": query_id})


# ===================================================================================== UC-10
def forward_query_to_tic(ctx: Ctx, admin_id, query_id, tic_id):
    # 1. Initial Type and Null Validation
    if admin_id is None or query_id is None or tic_id is None:
        return err("Validation Failed: Parameters cannot be null")
    if not is_str(admin_id) or not is_str(query_id) or not is_str(tic_id):
        return err("Validation Failed: Invalid parameter data types")
    # 2. Caller RBAC Validation (Must be Admin)
    try:
        admin_record = first(ctx.db.query(ROLE_SQL, [admin_id]))
        if not admin_record or admin_record["role_name"] != "Admin":
            return err("Security Error: Unauthorized access. Admin privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate caller permissions")
    # 3. Target User Validation (must be a TIC)
    try:
        tic_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not tic_record:
            return err("Database Error: Target user identity not found")
        if tic_record["role_name"] != "TIC":
            return err("Security Error: Cannot assign query. Target user is not a Teacher-in-Charge.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate target user role")
    # 4. Relational Integrity: Validate Query Existence
    try:
        target_query = first(ctx.db.query("SELECT status FROM D3_QUERIES WHERE query_id = ?", [query_id]))
        if not target_query:
            return err("Database Error: Target query reference not found")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query reference")
    # 5. Secure Database Transaction for Assignment and Audit
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.update("UPDATE D3_QUERIES SET assigned_tic = ?, status = ?, updated_at = ? WHERE query_id = ?",
                      [tic_id, "Assigned to TIC", current_time, query_id])
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                      "VALUES (?, ?, ?, ?, ?)", [admin_id, "Forward to TIC", "Query", query_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to assign query and commit audit log")
    # 6. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch(tic_id, "Query Assigned", query_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch assignment notification to TIC for query " + query_id)
    return success("Query successfully forwarded to TIC", {"query_id": query_id})


# ===================================================================================== UC-11
def knowledge_base_management(ctx: Ctx, admin_id, action_type, entry_data):
    # 1. Initial Type and Null Validation
    if admin_id is None or action_type is None or entry_data is None:
        return err("Validation Failed: Base parameters cannot be null")
    if not is_str(action_type) or not is_dict(entry_data):
        return err("Validation Failed: Invalid parameter data types")
    # 2. Explicit Action Type Validation
    valid_actions = ["Create", "Update", "Deactivate"]
    is_valid_action = False
    for i in range(len(valid_actions)):
        if action_type == valid_actions[i]:
            is_valid_action = True
            break
    if is_valid_action is False:
        return err("Validation Failed: Unrecognized action type")
    # 3. Strict Role-Based Access Control (RBAC)
    try:
        role_record = first(ctx.db.query(KB_ROLE_SQL, [admin_id]))
        if not role_record:
            return err("Database Error: User identity not found")
        if role_record["role_name"] != "Admin" and role_record["role_name"] != "Authorized TIC":
            return err("Security Error: Unauthorized modification attempt")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    current_time = ctx.now()
    # 4. Branch: Create Entry
    if action_type == "Create":
        if entry_data.get("title") is None or entry_data.get("content") is None:
            return err("Validation Failed: Title and content are required for creation")
        embedding_vector = None
        try:
            embedding_vector = ctx.gw.embedder.generate_embedding(entry_data["content"], "RETRIEVAL_DOCUMENT")
            if embedding_vector is None or len(embedding_vector) == 0:
                return err("API Error: Failed to generate vector embedding")
        except NetworkException as net_err:
            ctx.log_error(net_err)
            return err("System Error: AI Embedding service unavailable")
        new_kb_id = ctx.new_id()
        try:
            ctx.db.insert(
                "INSERT INTO D2_KNOWLEDGE (kb_id, title, content, category, source, verification_status, "
                "validity_status, embedding, created_by, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [new_kb_id, entry_data["title"], entry_data["content"], entry_data.get("category"),
                 entry_data.get("source"), "Verified", "Active", embedding_vector, admin_id, current_time,
                 current_time])
            return success("Knowledge Base entry created", {"kb_id": new_kb_id})
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to insert new KB entry")
    # 5. Branch: Update Entry
    elif action_type == "Update":
        if entry_data.get("kb_id") is None:
            return err("Validation Failed: KB ID required for update")
        try:
            existing_entry = first(ctx.db.query("SELECT content FROM D2_KNOWLEDGE WHERE kb_id = ?",
                                                [entry_data["kb_id"]]))
            if not existing_entry:
                return err("Database Error: Knowledge Base entry not found")
            update_query = "UPDATE D2_KNOWLEDGE SET title = ?, category = ?, source = ?, updated_at = ?"
            update_params = [entry_data.get("title"), entry_data.get("category"), entry_data.get("source"),
                             current_time]
            # Conditionally regenerate embeddings only if content changed
            if entry_data.get("content") is not None and entry_data["content"] != existing_entry["content"]:
                new_embedding = ctx.gw.embedder.generate_embedding(entry_data["content"], "RETRIEVAL_DOCUMENT")
                update_query = update_query + ", content = ?, embedding = ?"
                update_params.append(entry_data["content"])
                update_params.append(new_embedding)
            update_query = update_query + " WHERE kb_id = ?"
            update_params.append(entry_data["kb_id"])
            ctx.db.update(update_query, update_params)
            return success("Knowledge Base entry updated", {"kb_id": entry_data["kb_id"]})
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to update KB entry")
        except NetworkException as net_err:
            ctx.log_error(net_err)
            return err("System Error: AI Embedding service unavailable during update")
    # 6. Branch: Deactivate Entry
    elif action_type == "Deactivate":
        if entry_data.get("kb_id") is None:
            return err("Validation Failed: KB ID required for deactivation")
        try:
            rows_affected = ctx.db.update("UPDATE D2_KNOWLEDGE SET validity_status = ?, updated_at = ? "
                                          "WHERE kb_id = ?", ["Inactive", current_time, entry_data["kb_id"]])
            if rows_affected == 0:
                return err("Database Error: Target entry not found or already inactive")
            return success("Knowledge Base entry deactivated", {"kb_id": entry_data["kb_id"]})
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to deactivate KB entry")
