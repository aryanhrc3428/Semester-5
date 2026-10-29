"""Student-side use cases: UC-03 RaiseNewQuery, UC-04 LoadStudentDashboard,
UC-05 UploadDocument, UC-06 ViewRequestSlotAndAcceptMeeting.
Each procedure mirrors its pseudocode file (validation order, SQL, messages, transactions)."""
from ..core import (Ctx, DatabaseException, NetworkException, ROLE_SQL, err, first, is_dict, is_int, is_str,
                    success)


# ===================================================================================== UC-03
def raise_new_query(ctx: Ctx, student_id, query_text, department_id, category):
    # 1. Initial Type, Null, and Boundary Validation
    if student_id is None or query_text is None or department_id is None or category is None:
        return err("Validation Failed: Inputs cannot be null")
    if not is_str(query_text) or not is_str(category):
        return err("Validation Failed: Invalid data types")
    if len(query_text) < 10 or len(query_text) > 2000:
        return err("Validation Failed: Query text length out of bounds")
    # 2. Explicit Category Validation Loop
    valid_categories = ["Academic", "Administrative", "Technical", "Financial"]
    is_valid_category = False
    for i in range(len(valid_categories)):
        if category == valid_categories[i]:
            is_valid_category = True
            break
    if is_valid_category is False:
        return err("Validation Failed: Unrecognized query category")
    # 3. Relational Integrity Checks (Foreign Keys)
    try:
        student_record = ctx.db.query("SELECT user_id FROM USERS WHERE user_id = ?", [student_id])
        if not student_record:
            return err("Database Error: Invalid student identity")
        dept_record = ctx.db.query("SELECT dept_id FROM DEPARTMENTS WHERE dept_id = ?", [department_id])
        if not dept_record:
            return err("Database Error: Invalid department reference")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate relational constraints")
    # 4. Secure Database Transaction
    new_query_id = ctx.new_id()
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.insert(
            "INSERT INTO D3_QUERIES (query_id, student_id, department_id, description, category, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [new_query_id, student_id, department_id, query_text, category, "Open", current_time, current_time])
        ctx.db.insert(
            "INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            [student_id, "Create", "Query", new_query_id, current_time])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        return err("Database Error: Failed to save new query")
    # 5. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch("Admin", "New Query Escalated", new_query_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch notification for query " + new_query_id)
    return success("Query submitted successfully", {"query_id": new_query_id})


# ===================================================================================== UC-04
def load_student_dashboard(ctx: Ctx, student_id):
    # 1. Initial Type and Null Validation
    if student_id is None:
        return err("Validation Failed: Student ID cannot be null")
    if not is_str(student_id):
        return err("Validation Failed: Invalid data type for Student ID")
    # 2. Validate User Existence (Relational Integrity)
    try:
        auth_record = ctx.db.query("SELECT user_id FROM USERS WHERE user_id = ?", [student_id])
        if not auth_record:
            return err("Database Error: Student identity not found")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate user identity")
    # 3. Retrieve Base Queries (database engine does the sorting)
    try:
        student_queries = ctx.db.query("SELECT * FROM D3_QUERIES WHERE student_id = ? ORDER BY updated_at DESC",
                                       [student_id])
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("Database Error: Failed to retrieve student queries")
    if len(student_queries) == 0:
        return success("No queries found", [])
    # 4. Data Aggregation Loop (nested retrievals)
    dashboard_view = []
    for i in range(len(student_queries)):
        current_query = student_queries[i]
        associated_docs = []
        associated_meetings = []
        try:
            associated_docs = ctx.db.query(
                "SELECT document_id, file_name, status FROM D4_DOCUMENTS WHERE query_id = ?",
                [current_query["query_id"]])
            associated_meetings = ctx.db.query(
                "SELECT meeting_id, meeting_date AS date, start_time, status FROM D5_MEETINGS WHERE query_id = ?",
                [current_query["query_id"]])
        except DatabaseException:
            ctx.log_error("Warning: Failed to load relations for query " + current_query["query_id"])
            associated_docs = "Data unavailable"
            associated_meetings = "Data unavailable"
        # 5. Construct Compiled Record
        dashboard_view.insert(i, {"query_details": current_query, "documents": associated_docs,
                                  "meetings": associated_meetings})
    return success("Dashboard data retrieved successfully", dashboard_view)


# ===================================================================================== UC-05
def _extract_extension(name: str) -> str:
    return name.rsplit(".", 1)[1] if "." in name else ""


def upload_document(ctx: Ctx, student_id, query_id, file_obj):
    # 1. Initial Type and Null Validation
    if student_id is None or query_id is None or file_obj is None:
        return err("Validation Failed: Inputs cannot be null")
    if not is_str(getattr(file_obj, "name", None)) or not is_int(getattr(file_obj, "size", None)):
        return err("Validation Failed: Invalid file object structure")
    # 2. Explicit Physical File Constraints
    max_bytes = 25 * 1024 * 1024  # 26,214,400 bytes (25MB)
    if file_obj.size == 0 or file_obj.size > max_bytes:
        return err("Validation Failed: File size must be between 1 byte and 25MB")
    valid_formats = ["PDF", "JPG", "JPEG", "PNG"]
    file_extension = _extract_extension(file_obj.name).upper()
    is_valid_format = False
    for i in range(len(valid_formats)):
        if file_extension == valid_formats[i]:
            is_valid_format = True
            break
    if is_valid_format is False:
        return err("Validation Failed: Unsupported file format detected")
    # 3. Relational Integrity and Ownership Check
    try:
        parent_query = first(ctx.db.query("SELECT student_id, status FROM D3_QUERIES WHERE query_id = ?",
                                          [query_id]))
        if not parent_query:
            return err("Database Error: Invalid query reference")
        if parent_query["student_id"] != student_id:
            return err("Security Error: Unauthorized attempt to upload to another user's query")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate query ownership")
    # 4. External Cloud Storage Integration with Resilience
    storage_key = None
    try:
        storage_key = ctx.gw.storage.upload_stream(getattr(file_obj, "stream", None), file_obj.name, query_id)
        if storage_key is None:
            return err("Cloud Error: S3 returned null storage key")
    except NetworkException as net_err:
        ctx.log_error(net_err)
        return err("System Error: File upload service temporarily unavailable")
    # 5. Secure Database Transaction (Insert Document & Update Query)
    new_doc_id = ctx.new_id()
    current_time = ctx.now()
    try:
        ctx.db.begin()
        ctx.db.insert(
            "INSERT INTO D4_DOCUMENTS (document_id, query_id, uploaded_by, file_name, file_type, file_size, "
            "storage_key, status, uploaded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [new_doc_id, query_id, student_id, file_obj.name, file_extension, file_obj.size, storage_key,
             "Pending Review", current_time])
        ctx.db.update("UPDATE D3_QUERIES SET status = ?, updated_at = ? WHERE query_id = ?",
                      ["Document Submitted", current_time, query_id])
        ctx.db.commit()
    except DatabaseException as db_err:
        ctx.db.rollback()
        ctx.log_error(db_err)
        try:  # attempt to clean up the orphaned stored file
            ctx.gw.storage.delete(storage_key)
        except Exception as cleanup_err:  # noqa: BLE001 - cleanup must never mask the real error
            ctx.log_error(cleanup_err)
        return err("Database Error: Failed to save document records")
    # 6. Fire-and-Forget Asynchronous Notification
    try:
        ctx.dispatch("Staff", "Document Uploaded", new_doc_id)
    except NetworkException:
        ctx.log_error("Warning: Failed to dispatch staff notification for document " + new_doc_id)
    return success("Document securely uploaded and linked", {"document_id": new_doc_id})


# ===================================================================================== UC-06
def view_request_slot_and_accept_meeting(ctx: Ctx, user_id, action_type, slot_data):
    # 1. Initial Type and Null Validation
    if user_id is None or action_type is None or slot_data is None:
        return err("Validation Failed: Core parameters cannot be null")
    if not is_str(user_id) or not is_str(action_type) or not is_dict(slot_data):
        return err("Validation Failed: Invalid parameter data types")
    # 2. Explicit Action Type Validation Loop
    valid_actions = ["ViewSlots", "RequestSlot", "AcceptMeeting"]
    is_valid_action = False
    for i in range(len(valid_actions)):
        if action_type == valid_actions[i]:
            is_valid_action = True
            break
    if is_valid_action is False:
        return err("Validation Failed: Action must be 'ViewSlots', 'RequestSlot', or 'AcceptMeeting'")
    # 3. Strict Role-Based Access Control (RBAC) Validation
    try:
        role_record = first(ctx.db.query(ROLE_SQL, [user_id]))
        if not role_record:
            return err("Security Error: User account not found")
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to validate permissions")
    current_time = ctx.now()
    reference_id = None
    target_recipient_id = None
    notification_msg = ""
    # 4. Branch A: View Available Slots (Student or TIC)
    if action_type == "ViewSlots":
        if slot_data.get("tic_id") is None or slot_data.get("target_date") is None:
            return err("Validation Failed: TIC ID and target date required to view slots")
        try:
            available_slots = ctx.db.query(
                "SELECT slot_id, start_time, end_time, status FROM D6_TIME_SLOTS "
                "WHERE assigned_tic = ? AND slot_date = ? AND status = ?",
                [slot_data["tic_id"], slot_data["target_date"], "Available"])
            return success("Available slots retrieved successfully", available_slots)
        except DatabaseException as db_err:
            ctx.log_error(db_err)
            return err("Database Error: Failed to retrieve slot availability")
    # 5. Branch B: Request Slot (Student Action)
    elif action_type == "RequestSlot":
        if role_record["role_name"] != "Student":
            return err("Security Error: Only students can request meeting slots")
        if slot_data.get("slot_id") is None or slot_data.get("query_id") is None:
            return err("Validation Failed: Slot ID and Query ID required for request")
        try:
            target_slot = first(ctx.db.query("SELECT assigned_tic, status FROM D6_TIME_SLOTS WHERE slot_id = ?",
                                             [slot_data["slot_id"]]))
            if not target_slot or target_slot["status"] != "Available":
                return err("State Error: Selected slot is no longer available")
            target_recipient_id = target_slot["assigned_tic"]
            reference_id = slot_data["slot_id"]
            ctx.db.begin()
            ctx.db.update("UPDATE D6_TIME_SLOTS SET status = ?, student_id = ?, updated_at = ? WHERE slot_id = ?",
                          ["Requested", user_id, current_time, reference_id])
            ctx.db.insert(
                "INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                "VALUES (?, ?, ?, ?, ?)", [user_id, "Request Slot", "Slot", reference_id, current_time])
            ctx.db.commit()
            notification_msg = "Meeting Slot Requested"
        except DatabaseException as db_err:
            ctx.db.rollback()
            ctx.log_error(db_err)
            return err("Database Error: Failed to process slot request securely")
    # 6. Branch C: Accept Meeting (TIC Action)
    elif action_type == "AcceptMeeting":
        if role_record["role_name"] != "TIC":
            return err("Security Error: Only TICs can accept meeting slots")
        if slot_data.get("slot_id") is None:
            return err("Validation Failed: Slot ID required to accept meeting")
        try:
            target_slot = first(ctx.db.query(
                "SELECT assigned_tic, student_id, status FROM D6_TIME_SLOTS WHERE slot_id = ?",
                [slot_data["slot_id"]]))
            if not target_slot:
                return err("Database Error: Slot reference not found")
            if target_slot["assigned_tic"] != user_id:
                return err("Security Error: Unauthorized attempt to accept another TIC's slot")
            if target_slot["status"] != "Requested":
                return err("State Error: Slot must be in 'Requested' state to accept")
            target_recipient_id = target_slot["student_id"]
            reference_id = slot_data["slot_id"]
            ctx.db.begin()
            ctx.db.update("UPDATE D6_TIME_SLOTS SET status = ?, updated_at = ? WHERE slot_id = ?",
                          ["Accepted", current_time, reference_id])
            ctx.db.insert(
                "INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                "VALUES (?, ?, ?, ?, ?)", [user_id, "Accept Meeting", "Slot", reference_id, current_time])
            ctx.db.commit()
            notification_msg = "Meeting Accepted"
        except DatabaseException as db_err:
            ctx.db.rollback()
            ctx.log_error(db_err)
            return err("Database Error: Failed to accept meeting slot safely")
    # 7. Fire-and-Forget Asynchronous Notification
    if action_type != "ViewSlots":
        try:
            ctx.dispatch(target_recipient_id, notification_msg, reference_id)
        except NetworkException:
            ctx.log_error("Warning: Failed to dispatch notification for slot " + reference_id)
    return success("Action successfully processed: " + action_type, {"reference_id": reference_id})
