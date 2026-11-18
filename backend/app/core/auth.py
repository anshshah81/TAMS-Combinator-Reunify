import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import select
from ..models import AuthSession, User

COOKIE = 'reunify_demo_session'
CSRF_HEADER = 'x-reunify-csrf'


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_db(request: Request):
    with request.app.state.session_factory() as db:
        yield db


def get_settings(request: Request):
    return request.app.state.settings


def get_storage(request: Request):
    return request.app.state.storage


def require_demo_auth(request: Request):
    if not request.app.state.settings.demo_auth:
        raise HTTPException(503, 'Demo sign-in is disabled.')


def require_csrf(request: Request):
    """Reject cross-site mutations: enforce a same-origin header and a custom
    header that browsers cannot set cross-origin without an allowed CORS policy.
    This demo portal only accepts a single loopback frontend origin."""
    settings = request.app.state.settings
    origin = request.headers.get('origin')
    if origin is not None and origin != settings.frontend_origin:
        raise HTTPException(403, 'Cross-origin request rejected.')
    if request.headers.get(CSRF_HEADER) != '1':
        raise HTTPException(403, 'Missing request verification header.')


def create_session(db, user_id: str, settings) -> str:
    """Issue an opaque random session token; only its hash and expiry persist."""
    token = secrets.token_urlsafe(32)
    db.add(AuthSession(
        token_hash=token_hash(token),
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.session_seconds),
    ))
    db.commit()
    return token


def set_session_cookie(response: Response, token: str, settings) -> None:
    response.set_cookie(
        COOKIE, token, max_age=settings.session_seconds, httponly=True,
        samesite='strict', secure=False, path='/',
    )


def clear_session(db, token: str, response: Response) -> None:
    if token:
        session = db.get(AuthSession, token_hash(token))
        if session is not None:
            db.delete(session)
            db.commit()
    response.delete_cookie(COOKIE, path='/')


def current_user(request: Request, db=Depends(get_db)) -> User:
    if not request.app.state.settings.demo_auth:
        raise HTTPException(503, 'Demo sign-in is disabled.')
    token = request.cookies.get(COOKIE, '')
    session = db.get(AuthSession, token_hash(token)) if token else None
    if not session or session.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(401, 'Sign in to continue.')
    user = db.scalar(select(User).where(User.id == session.user_id, User.active.is_(True)))
    if not user:
        raise HTTPException(401, 'Sign in to continue.')
    return user


def roles(*allowed):
    def permitted(user=Depends(current_user)):
        if user.role not in allowed:
            raise HTTPException(403, 'This account cannot perform this action.')
        return user
    return permitted
