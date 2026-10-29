"""UC-07 DispatchNotificationAsync -- mirrors pseudocode/UC-07.pseudo.
(The 'Async' part is provided by the caller: see app/runtime.py which runs this procedure on a
worker thread so the triggering use case never blocks on email delivery.)"""
from ..core import Ctx, DatabaseException, NetworkException, err, first, is_str, success

VALID_EVENTS = ["New Query Escalated", "Query Assigned", "Query Resolved", "Document Required",
                "Document Uploaded", "Document Accepted", "Document Rejected", "Meeting Scheduled",
                "Meeting Cancelled"]


def dispatch_notification(ctx: Ctx, target, event_type, reference_id):
    # 1. Initial Type and Null Validation
    if target is None or event_type is None or reference_id is None:
        return err("Validation Failed: Inputs cannot be null")
    if not is_str(target) or not is_str(event_type):
        return err("Validation Failed: Invalid data types")
    # 2. Validate Event Type
    is_valid_event = False
    for i in range(len(VALID_EVENTS)):
        if event_type == VALID_EVENTS[i]:
            is_valid_event = True
            break
    if is_valid_event is False:
        return err("Validation Failed: Unrecognized event type")
    # 3. Resolve Target to Email Addresses
    recipient_emails = []
    try:
        if target == "Admin" or target == "TIC" or target == "Staff":
            role_query = "SELECT U.email FROM USERS U JOIN ROLE R ON U.role_id = R.role_id WHERE R.role_name = ?"
            if target == "Staff":
                role_query = ("SELECT U.email FROM USERS U JOIN ROLE R ON U.role_id = R.role_id "
                              "WHERE R.role_name IN ('Admin', 'TIC')")
                role_records = ctx.db.query(role_query, [])
            else:
                role_records = ctx.db.query(role_query, [target])
            for record in role_records:
                recipient_emails.append(record["email"])
        else:
            user_record = first(ctx.db.query("SELECT email FROM USERS WHERE user_id = ?", [target]))
            if user_record:
                recipient_emails.append(user_record["email"])
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("Database Error: Failed to resolve target email addresses")
    if len(recipient_emails) == 0:
        return err("Resolution Error: No valid email addresses found for target")
    # 4. Construct Email Content
    email_subject = "System Notification: " + event_type
    email_body = ("An event '" + event_type + "' has occurred concerning reference ID: " + str(reference_id)
                  + ". Please log in to your dashboard to view details.")
    # 5. Dispatch Loop with Individual Error Handling
    success_count = 0
    failure_count = 0
    current_time = ctx.now()
    for email_address in recipient_emails:
        try:
            api_response = ctx.gw.email.send(email_address, email_subject, email_body)
            if api_response.status_code == 200:
                success_count += 1
                try:
                    ctx.db.insert(
                        "INSERT INTO D7_AUDIT_LOGS (user_id, action_type, entity, entity_id, timestamp) "
                        "VALUES (?, ?, ?, ?, ?)",
                        ["System", "Email Sent to " + email_address, "Notification", reference_id, current_time])
                except DatabaseException:
                    ctx.log_error("Warning: Failed to log notification success for " + email_address)
            else:
                failure_count += 1
                ctx.log_error("Email API Error: Failed to send to " + email_address + " with status "
                              + str(api_response.status_code))
        except NetworkException:
            failure_count += 1
            ctx.log_error("Network Error: Could not reach email service for " + email_address)
    if success_count > 0:
        return success("Dispatched " + str(success_count) + " notifications. Failures: " + str(failure_count))
    return err("Dispatch Failed: Unable to send any notifications")
