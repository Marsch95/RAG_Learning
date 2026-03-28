"""Authentication service for the fictional Acme Checkout backend."""

from __future__ import annotations


class AuthService:
    def login(self, username: str, password: str) -> dict[str, str]:
        if not validate_credentials(username, password):
            return {"status": "error", "message": "Invalid username or password."}

        session_token = create_session_token(username)
        record_login_audit(username, role="cashier")
        return {"status": "ok", "session_token": session_token}


def validate_credentials(username: str, password: str) -> bool:
    return username == "cashier-01" and password == "register-pass"


def create_session_token(username: str) -> str:
    return f"session-{username}-token"


def record_login_audit(username: str, role: str) -> str:
    return f"audit:{username}:{role}"
