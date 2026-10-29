import pytest
from types import SimpleNamespace as NS

from app.usecases.auth import authenticate
from .helpers import DB_ERR, NET_ERR, FakeDb, Seq, make_ctx

OK = lambda ident="ident-1": NS(status_code=200, user_identity=ident)  # noqa: E731
BAD = NS(status_code=401, user_identity=None)


class Auth:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    def call(self, u, p):
        o = self.outcomes[min(self.calls, len(self.outcomes) - 1)]
        self.calls += 1
        if isinstance(o, Exception):
            raise o
        return o


class Jwt:
    def generate(self, uid, role_name, ttl):
        return f"jwt:{uid}:{role_name}:{ttl}"


def ctx_for(auth, db=None):
    return make_ctx(db or FakeDb(), auth=auth, jwt=Jwt())


@pytest.mark.parametrize("u,p,expected", [
    (None, "SecurePass123", "Validation Failed: Credentials cannot be null"),
    ("student01", None, "Validation Failed: Credentials cannot be null"),
    (10492, "SecurePass123", "Validation Failed: Invalid data type"),
    ("student01", 12345, "Validation Failed: Invalid data type"),
    ("abcd", "pw", "Validation Failed: Username length out of bounds"),
    ("a" * 51, "pw", "Validation Failed: Username length out of bounds"),
    ("stu;dent1", "pw", "Validation Failed: Illegal characters detected"),
    ("stu-dent1", "pw", "Validation Failed: Illegal characters detected"),
    ('stu"dent1', "pw", "Validation Failed: Illegal characters detected"),
    ("stu'dent1", "pw", "Validation Failed: Illegal characters detected"),
])
def test_validation_rejects_before_any_external_call(u, p, expected):
    auth = Auth(OK())
    db = FakeDb()
    r = authenticate(ctx_for(auth, db), u, p)
    assert r.is_error and r.message == expected and r.http_status == 400
    assert auth.calls == 0 and db.calls == []


@pytest.mark.parametrize("username", ["abcde", "a" * 50])
def test_username_length_boundaries_accepted(username):
    from .helpers import role
    db = FakeDb().on("FROM USERS", [{"user_id": "U1", "role_id": 1}]).on("FROM ROLE", role("Student"))
    assert authenticate(ctx_for(Auth(OK()), db), username, "pw").is_success


def test_success_returns_token_user_role_and_dashboard():
    from .helpers import role
    db = FakeDb().on("FROM USERS", [{"user_id": "U1", "role_id": 2}]).on("FROM ROLE", role("Admin"))
    r = authenticate(ctx_for(Auth(OK("ident-9")), db), "admin.office", "pw")
    assert r.is_success
    assert r.data == {"session_token": "jwt:U1:Admin:3600", "user_id": "U1", "role_name": "Admin",
                      "dashboard_url": "/Admin/dashboard"}
    assert db.calls[0][2] == ["ident-9"]          # parameterized lookup by external identity


def test_retries_on_failed_status_then_succeeds():
    from .helpers import role
    db = FakeDb().on("FROM USERS", [{"user_id": "U1", "role_id": 1}]).on("FROM ROLE", role("Student"))
    auth = Auth(BAD, NET_ERR, OK())
    assert authenticate(ctx_for(auth, db), "student01", "pw").is_success
    assert auth.calls == 3


@pytest.mark.parametrize("outcomes", [(BAD,), (NET_ERR,), (BAD, NET_ERR, BAD)])
def test_three_failed_attempts_fail_authentication(outcomes):
    auth = Auth(*outcomes)
    r = authenticate(ctx_for(auth), "student01", "pw")
    assert r.message == "Authentication Failed: Maximum attempts exceeded or service unavailable"
    assert r.http_status == 401 and auth.calls == 3


def test_local_account_missing():
    db = FakeDb().on("FROM USERS", [])
    r = authenticate(ctx_for(Auth(OK()), db), "student01", "pw")
    assert r.message == "Database Error: User verified externally but local account missing"
    assert r.http_status == 403


def test_role_missing():
    db = FakeDb().on("FROM USERS", [{"user_id": "U1", "role_id": 7}]).on("FROM ROLE", [])
    r = authenticate(ctx_for(Auth(OK()), db), "student01", "pw")
    assert r.message == "Database Error: User lacks assigned system role"


@pytest.mark.parametrize("fragment", ["FROM USERS", "FROM ROLE"])
def test_database_exception_is_logged_and_generic(fragment):
    db = FakeDb()
    if fragment == "FROM ROLE":
        db.on("FROM USERS", [{"user_id": "U1", "role_id": 1}])
    db.on(fragment, DB_ERR)
    ctx = ctx_for(Auth(OK()), db)
    r = authenticate(ctx, "student01", "pw")
    assert r.message == "System Error: Unable to complete authentication transaction"
    assert ctx.logs and "simulated database failure" in ctx.logs[0]
