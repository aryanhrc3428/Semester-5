"""Teacher-in-Charge use cases: UC-12 TICViewAssignedQueries, UC-13 TICResolveQuery,
UC-14 TICRequestDocument, UC-15 TICReviewDocument, UC-16 ViewTimetable (external),
UC-17 ManageMeeting. Mirrors the pseudocode files."""
from ..core import (Ctx, DatabaseException, NetworkException, ROLE_SQL, SystemException, err, first, is_bool,
                    is_dict, is_str, success)
from .admin import knowledge_base_management


# ===================================================================================== UC-12
def tic_view_assigned_queries(ctx: Ctx, tic_id):
    # 1. Initial Type and Null Validation
    if tic_id is None:
        return err("Validation Failed: TIC ID cannot be null")
    if not is_str(tic_id):
        return err("Validation Failed: Invalid data type for TIC ID")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record:
            return err("Database Error: User identity not found")
        if role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Secure Base Query Retrieval (filtered by ownership)
    try:
        assigned_queries = ctx.db.query("SELECT * FROM D3_QUERIES WHERE assigned_tic = ? ORDER BY updated_at DESC",
                                        [tic_id])
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("Database Error: Failed to retrieve assigned queries")
    if len(assigned_queries) == 0:
        return success("No assigned queries found", [])
    # 4. Data Aggregation Loop for Dashboard Context
    tic_dashboard_view = []
    for i in range(len(assigned_queries)):
        current_query = assigned_queries[i]
        student_details = {}
        try:
            student_record = first(ctx.db.query("SELECT name, email, department_id FROM USERS WHERE user_id = ?",
                                                [current_query["student_id"]]))
            if student_record:
                student_details["name"] = student_record["name"]
                student_details["email"] = student_record["email"]
                student_details["department_id"] = student_record["department_id"]
            else:
                student_details["name"] = "Unknown Student"
                student_details["email"] = "Unknown Email"
                student_details["department_id"] = "Unknown"
        except DatabaseException:
            ctx.log_error("Warning: Failed to load student details for query " + current_query["query_id"])
            student_details["name"] = "Data unavailable"
            student_details["email"] = "Data unavailable"
            student_details["department_id"] = "Data unavailable"
        # 5. Construct Compiled Record
        tic_dashboard_view.insert(i, {"query_details": current_query, "student_info": student_details})
    return success("TIC dashboard data retrieved successfully", tic_dashboard_view)


# ===================================================================================== UC-13
def tic_resolve_query(ctx: Ctx, tic_id, query_id, resolution_text, add_to_kb_flag):
    # 1. Initial Type, Null, and Boundary Validation
    if tic_id is None or query_id is None or resolution_text is None or add_to_kb_flag is None:
        return err("Validation Failed: Parameters cannot be null")
    if (not is_str(tic_id) or not is_str(query_id) or not is_str(resolution_text)
            or not is_bool(add_to_kb_flag)):
        return err("Validation Failed: Invalid parameter data types")
    if len(resolution_text) < 10 or len(resolution_text) > 5000:
        return err("Validation Failed: Resolution text length out of bounds")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record or role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Explicit Ownership and Integrity Validation (IDOR prevention)
    try:
        target_query = first(ctx.db.query(
            "SELECT assigned_tic, student_id, description, category FROM D3_QUERIES WHERE query_id = ?",
            [query_id]))
        if not target_query:
            return err("Database Error: Target query reference not found")
        if target_query["assigned_tic"] != tic_id:
            return err("Security Error: Unauthorized. You can only resolve queries explicitly assigned to you.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query ownership")
    # 4. Secure Database Transaction for Resolution and Audit
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.update("UPDATE D3_QUERIES SET status = ?, resolution = ?, resolved_by = ?, updated_at = ? "
                      "WHERE query_id = ?", ["Resolved", resolution_text, tic_id, current_time, query_id])
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                      "VALUES (?, ?, ?, ?, ?)", [tic_id, "Resolve", "Query", query_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to resolve query and commit audit log")
    # 5. Conditional Knowledge Base Escalation (isolated from main transaction)
    if add_to_kb_flag is True:
        try:
            kb_payload = {"title": target_query["description"], "content": resolution_text,
                          "category": target_query["category"], "source": "TIC Resolution - " + tic_id}
            kb_result = (ctx.kb_manage or knowledge_base_management)(ctx, tic_id, "Create", kb_payload)
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


# ===================================================================================== UC-14
def tic_request_document(ctx: Ctx, tic_id, query_id, doc_note):
    # 1. Initial Type, Null, and Boundary Validation
    if tic_id is None or query_id is None or doc_note is None:
        return err("Validation Failed: Parameters cannot be null")
    if not is_str(tic_id) or not is_str(query_id) or not is_str(doc_note):
        return err("Validation Failed: Invalid parameter data types")
    if len(doc_note) < 5 or len(doc_note) > 1000:
        return err("Validation Failed: Document request note length out of bounds")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record or role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Explicit Ownership and State Validation (IDOR prevention)
    try:
        target_query = first(ctx.db.query("SELECT assigned_tic, student_id, status FROM D3_QUERIES "
                                          "WHERE query_id = ?", [query_id]))
        if not target_query:
            return err("Database Error: Target query reference not found")
        if target_query["assigned_tic"] != tic_id:
            return err("Security Error: Unauthorized. You can only manage queries explicitly assigned to you.")
        if target_query["status"] == "Resolved" or target_query["status"] == "Closed":
            return err("State Error: Cannot request documents for a closed or resolved query.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query ownership and state")
    # 4. Secure Database Transaction for State Transition and Audit
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.update("UPDATE D3_QUERIES SET status = ?, doc_request_note = ?, updated_at = ? WHERE query_id = ?",
                      ["Documents Required", doc_note, current_time, query_id])
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                      "VALUES (?, ?, ?, ?, ?)", [tic_id, "Request Document", "Query", query_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to update query state and commit audit log")
    # 5. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch(target_query["student_id"], "Document Required", query_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch document request notification to student for query "
                      + query_id)
    return success("Document request successfully logged and student notified", {"query_id": query_id})


# ===================================================================================== UC-15
def tic_review_document(ctx: Ctx, tic_id, query_id, doc_id, review_decision, review_notes=None):
    # 1. Initial Type and Null Validation
    if tic_id is None or query_id is None or doc_id is None or review_decision is None:
        return err("Validation Failed: Core parameters cannot be null")
    if (not is_str(tic_id) or not is_str(query_id) or not is_str(doc_id) or not is_str(review_decision)):
        return err("Validation Failed: Invalid parameter data types")
    # 2. Explicit Decision Validation Loop
    valid_decisions = ["Accept", "Reject"]
    is_valid_decision = False
    for i in range(len(valid_decisions)):
        if review_decision == valid_decisions[i]:
            is_valid_decision = True
            break
    if is_valid_decision is False:
        return err("Validation Failed: Decision must be 'Accept' or 'Reject'")
    # Rejections require a justification
    if review_decision == "Reject" and (review_notes is None or len(review_notes) < 5):
        return err("Validation Failed: Rejection requires detailed review notes")
    # 3. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record or role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 4. Explicit Ownership and State Validation (IDOR prevention)
    try:
        target_query = first(ctx.db.query("SELECT assigned_tic, student_id FROM D3_QUERIES WHERE query_id = ?",
                                          [query_id]))
        if not target_query:
            return err("Database Error: Target query reference not found")
        if target_query["assigned_tic"] != tic_id:
            return err("Security Error: Unauthorized. You can only review documents for queries assigned to you.")
        target_doc = first(ctx.db.query("SELECT status FROM D4_DOCUMENTS WHERE document_id = ? AND query_id = ?",
                                        [doc_id, query_id]))
        if not target_doc:
            return err("Database Error: Document not found or does not belong to the specified query")
        if target_doc["status"] != "Pending Review":
            return err("State Error: Document is not in a reviewable state")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query and document integrity")
    # 5. Secure Database Transaction for Dual-State Transition
    current_time = ctx.now()
    notification_type = ""
    try:
        ctx.db.begin()
        doc_update = ("UPDATE D4_DOCUMENTS SET status = ?, review_notes = ?, updated_at = ? "
                      "WHERE document_id = ?")
        query_update = "UPDATE D3_QUERIES SET status = ?, updated_at = ? WHERE query_id = ?"
        if review_decision == "Accept":
            ctx.db.update(doc_update, ["Verified", review_notes, current_time, doc_id])
            ctx.db.update(query_update, ["Assigned to TIC", current_time, query_id])
            notification_type = "Document Accepted"
        elif review_decision == "Reject":
            ctx.db.update(doc_update, ["Rejected", review_notes, current_time, doc_id])
            ctx.db.update(query_update, ["Documents Required", current_time, query_id])
            notification_type = "Document Rejected"
        ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                      "VALUES (?, ?, ?, ?, ?)",
                      [tic_id, "Review Document - " + review_decision, "Document", doc_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to update document and query states")
    # 6. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch(target_query["student_id"], notification_type, query_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch document review notification to student for query " + query_id)
    return success("Document successfully " + review_decision + "ed", {"document_id": doc_id})


# ===================================================================================== UC-16
def view_timetable_availability(ctx: Ctx, tic_id, target_date):
    # 1. Initial Type, Null, and Boundary Validation
    if tic_id is None or target_date is None:
        return err("Validation Failed: Parameters cannot be null")
    if not is_str(tic_id) or not is_str(target_date):
        return err("Validation Failed: Invalid parameter data types")
    if len(target_date) != 10:
        return err("Validation Failed: Invalid date format, expected YYYY-MM-DD")
    # 2. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record or role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    # 3. Resilient External Timetable Fetch
    base_schedule = []
    try:
        base_schedule = ctx.gw.timetable.fetch(tic_id, target_date)
        if base_schedule is None:
            return err("API Error: Timetable service returned a null schedule")
    except NetworkException as net_err:
        ctx.log_error(net_err)
        return err("System Error: External timetable service is temporarily unavailable")
    # Empty base schedule (weekend/holiday): return early
    if len(base_schedule) == 0:
        return success("No slots available on this date", [])
    # 4. Secure Database Retrieval of Existing Bookings
    try:
        booked_meetings = ctx.db.query(
            "SELECT start_time, end_time FROM D5_MEETINGS WHERE assigned_tic = ? AND meeting_date = ? "
            "AND status != ?", [tic_id, target_date, "Cancelled"])
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("Database Error: Failed to retrieve existing meeting bookings")
    # 5. Explicit Algorithmic Conflict Resolution (nested loops)
    available_slots = []
    for i in range(len(base_schedule)):
        current_slot = base_schedule[i]
        has_conflict = False
        for j in range(len(booked_meetings)):
            booked_slot = booked_meetings[j]
            # Two intervals overlap if (Start1 < End2) AND (End1 > Start2)
            if (current_slot["start_time"] < booked_slot["end_time"]
                    and current_slot["end_time"] > booked_slot["start_time"]):
                has_conflict = True
                break
        if has_conflict is False:
            available_slots.append(current_slot)
    return success("Timetable availability calculated successfully", available_slots)


# ===================================================================================== UC-17
def manage_meeting(ctx: Ctx, tic_id, action_type, meeting_data):
    # 1. Initial Type and Null Validation
    if tic_id is None or action_type is None or meeting_data is None:
        return err("Validation Failed: Core parameters cannot be null")
    if not is_str(tic_id) or not is_str(action_type) or not is_dict(meeting_data):
        return err("Validation Failed: Invalid parameter data types")
    # 2. Explicit Action Type Validation Loop
    valid_actions = ["Schedule", "Cancel"]
    is_valid_action = False
    for i in range(len(valid_actions)):
        if action_type == valid_actions[i]:
            is_valid_action = True
            break
    if is_valid_action is False:
        return err("Validation Failed: Action must be 'Schedule' or 'Cancel'")
    # 3. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [tic_id]))
        if not role_record or role_record["role_name"] != "TIC":
            return err("Security Error: Unauthorized access. TIC privileges required.")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    current_time = ctx.now()
    student_id_target = None
    reference_id = None
    notification_type = ""
    # 4. Branch A: Schedule Meeting
    if action_type == "Schedule":
        if (meeting_data.get("query_id") is None or meeting_data.get("date") is None
                or meeting_data.get("start_time") is None or meeting_data.get("end_time") is None):
            return err("Validation Failed: Incomplete meeting scheduling data")
        try:
            target_query = first(ctx.db.query("SELECT assigned_tic, student_id FROM D3_QUERIES WHERE query_id = ?",
                                              [meeting_data["query_id"]]))
            if not target_query or target_query["assigned_tic"] != tic_id:
                return err("Security Error: Cannot schedule meeting for an unassigned or invalid query")
            student_id_target = target_query["student_id"]
            # Concurrency control: (existing_start < new_end) AND (existing_end > new_start)
            conflict_record = ctx.db.query(
                "SELECT meeting_id FROM D5_MEETINGS WHERE assigned_tic = ? AND meeting_date = ? AND status != ? "
                "AND start_time < ? AND end_time > ?",
                [tic_id, meeting_data["date"], "Cancelled", meeting_data["end_time"], meeting_data["start_time"]])
            if conflict_record:
                return err("Concurrency Error: Time slot has already been booked (Race Condition Prevented)")
            reference_id = ctx.new_id()
            ctx.db.begin()
            ctx.db.insert(
                "INSERT INTO D5_MEETINGS (meeting_id, query_id, assigned_tic, student_id, meeting_date, "
                "start_time, end_time, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [reference_id, meeting_data["query_id"], tic_id, student_id_target, meeting_data["date"],
                 meeting_data["start_time"], meeting_data["end_time"], "Scheduled", current_time])
            ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                          "VALUES (?, ?, ?, ?, ?)",
                          [tic_id, "Schedule Meeting", "Meeting", reference_id, current_time])
            ctx.db.commit()
            notification_type = "Meeting Scheduled"
        except DatabaseException as db_err:
            ctx.db.rollback()
            ctx.log_error(db_err)
            return err("Database Error: Failed to schedule meeting safely")
    # 5. Branch B: Cancel Meeting
    elif action_type == "Cancel":
        if meeting_data.get("meeting_id") is None:
            return err("Validation Failed: Meeting ID required for cancellation")
        reference_id = meeting_data["meeting_id"]
        try:
            target_meeting = first(ctx.db.query(
                "SELECT assigned_tic, student_id, status FROM D5_MEETINGS WHERE meeting_id = ?", [reference_id]))
            if not target_meeting:
                return err("Database Error: Meeting reference not found")
            if target_meeting["assigned_tic"] != tic_id:
                return err("Security Error: Unauthorized attempt to cancel another TIC's meeting")
            if target_meeting["status"] == "Cancelled":
                return err("State Error: Meeting is already cancelled")
            student_id_target = target_meeting["student_id"]
            ctx.db.begin()
            ctx.db.update("UPDATE D5_MEETINGS SET status = ?, updated_at = ? WHERE meeting_id = ?",
                          ["Cancelled", current_time, reference_id])
            ctx.db.insert("INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                          "VALUES (?, ?, ?, ?, ?)",
                          [tic_id, "Cancel Meeting", "Meeting", reference_id, current_time])
            ctx.db.commit()
            notification_type = "Meeting Cancelled"
        except DatabaseException as db_err:
            ctx.db.rollback()
            ctx.log_error(db_err)
            return err("Database Error: Failed to cancel meeting safely")
    # 6. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch(student_id_target, notification_type, reference_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch meeting notification to student for meeting " + reference_id)
    # The pseudocode concatenates action_type + "d"; the test suite (UC-17) expects the correctly
    # spelled past tense "Cancelled" for Cancel, "Scheduled" for Schedule.
    past = "Scheduled" if action_type == "Schedule" else "Cancelled"
    return success("Meeting successfully " + past, {"meeting_id": reference_id})
