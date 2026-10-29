"""UC-01 Authenticate -- mirrors pseudocode/UC-01.pseudo step for step."""
from ..core import (Ctx, DatabaseException, NetworkException, err, first, is_str, success)


def authenticate(ctx: Ctx, username, password):
    # 1. Initial Type and Null Validation
    if username is None or password is None:
        return err("Validation Failed: Credentials cannot be null")
    if not is_str(username) or not is_str(password):
        return err("Validation Failed: Invalid data type")
    # 2. Boundary Validation
    if len(username) < 5 or len(username) > 50:
        return err("Validation Failed: Username length out of bounds")
    # 3. Character Sanitization Loop
    forbidden_chars = [";", "-", '"', "'"]
    for i in range(len(username)):
        if username[i] in forbidden_chars:
            return err("Validation Failed: Illegal characters detected")
    # 4. Resilient External Call with Error Handling
    retry_count = 0
    is_authenticated = False
    auth_id = None
    while retry_count < 3 and is_authenticated is False:
        try:
            response = ctx.gw.auth.call(username, password)
            if response.status_code == 200:
                is_authenticated = True
                auth_id = response.user_identity
            else:
                retry_count += 1
        except NetworkException:
            retry_count += 1
    if is_authenticated is False:
        return err("Authentication Failed: Maximum attempts exceeded or service unavailable")
    # 5. Secure Parameterized Database Queries
    try:
        user_record = first(ctx.db.query("SELECT user_id, role_id FROM USERS WHERE user_identity = ?", [auth_id]))
        if not user_record:
            return err("Database Error: User verified externally but local account missing")
        role_record = first(ctx.db.query("SELECT role_name FROM ROLE WHERE role_id = ?", [user_record["role_id"]]))
        if not role_record:
            return err("Database Error: User lacks assigned system role")
        # 6. Token Generation and Routing
        session_token = ctx.gw.jwt.generate(user_record["user_id"], role_record["role_name"], 3600)
        dashboard_url = "/" + role_record["role_name"] + "/dashboard"
        return success("Authentication successful", {
            "session_token": session_token, "user_id": user_record["user_id"],
            "role_name": role_record["role_name"], "dashboard_url": dashboard_url})
    except DatabaseException as db_err:
        ctx.log_error(db_err)
        return err("System Error: Unable to complete authentication transaction")
