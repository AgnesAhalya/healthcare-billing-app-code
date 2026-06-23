import time
from dataclasses import dataclass
from functools import wraps
from flask import request, g, session, redirect, url_for
import jwt
from werkzeug.security import check_password_hash

from shared.extensions import (
    EXPIRY_TIME,
    JWT_ISSUER,
    JWT_AUDIENCE,
    PRIVATE_KEY_PEM,
    PUBLIC_KEY_PEM
)
from db.database import (
    find_user_by_username,
    create_login_session,
    find_active_session,
    revoke_active_sessions_for_user
)


@dataclass
class CurrentSession:
    session_id: str
    user_id: str
    user_type: str


def create_token(user):
    now = int(time.time())
    
    revoke_active_sessions_for_user(
        user["user_id"],
        user["user_type"]
    )
    session_id = create_login_session(
        user["user_id"],
        user["user_type"],
        EXPIRY_TIME
    )

    payload = {
        "sid": session_id,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + EXPIRY_TIME
    }

    return jwt.encode(
        payload,
        PRIVATE_KEY_PEM,
        algorithm="RS256"
    )


def authenticate(username, password, expected_user_type):
    user = find_user_by_username(username)

    if user is None:
        return None

    if user["user_type"] != expected_user_type:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return user


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.removeprefix("Bearer ").strip()


def load_current_session(token, expected_user_type):
    payload = jwt.decode(
        token,
        PUBLIC_KEY_PEM,
        algorithms=["RS256"],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE
    )

    session_id = payload.get("sid")

    if session_id is None:
        return None

    session = find_active_session(session_id)

    if session is None:
        return None

    if session["user_type"] != expected_user_type:
        return None

    return CurrentSession(
        session_id=session["session_id"],
        user_id=session["user_id"],
        user_type=session["user_type"]
    )

def require_role(expected_user_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            token = session.get("access_token")
            usertype = session.get("usertype")
            if token is None or usertype != expected_user_type:
                return redirect(url_for("patient_002.login_page"))
            try:
                current_session = load_current_session(token, expected_user_type)
            except jwt.PyJWTError:
                session.clear()
                return redirect(url_for("patient_002.login_page"))
            if current_session is None:
                session.clear()
                return redirect(url_for("patient_002.login_page"))
            g.current_session = current_session
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(view_func):
    from functools import wraps
    from flask import g, redirect, session, url_for
    from auth.session_service import load_current_session

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        token = session.get("access_token")
        usertype = session.get("usertype")
        if token is None or usertype is None:
            return redirect(url_for("patient_002.login_page"))
        current_session = load_current_session(token, usertype)
        if current_session is None:
            session.clear()
            return redirect(url_for("patient_002.login_page"))
        g.current_session = current_session
        return view_func(*args, **kwargs)
    return wrapper
