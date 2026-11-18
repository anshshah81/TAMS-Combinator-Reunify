"""Development-only demo authentication.

This is NOT production security: it lets a visitor assume a fictional seeded
identity to exercise role-based access. It is disabled unless APP_ENV is
development and DEMO_AUTH_ENABLED is true.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from ..core.auth import (COOKIE, clear_session, create_session, current_user,
                         get_db, get_settings, require_csrf, require_demo_auth,
                         set_session_cookie)
from ..intake_schemas import DemoAccountOut, LoginIn, UserOut
from ..models import User

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.get('/demo-accounts', response_model=list[DemoAccountOut],
            dependencies=[Depends(require_demo_auth)])
def demo_accounts(db=Depends(get_db)):
    users = db.scalars(select(User).where(User.active.is_(True)).order_by(User.id)).all()
    return users


@router.post('/login', response_model=UserOut,
             dependencies=[Depends(require_demo_auth), Depends(require_csrf)])
def login(payload: LoginIn, response: Response, request: Request, db=Depends(get_db)):
    user = db.scalar(select(User).where(User.id == payload.user_id, User.active.is_(True)))
    if user is None:
        # Do not reveal whether the identifier exists.
        raise HTTPException(401, 'Unknown demo account.')
    token = create_session(db, user.id, get_settings(request))
    set_session_cookie(response, token, get_settings(request))
    return user


@router.post('/logout', dependencies=[Depends(require_demo_auth), Depends(require_csrf)])
def logout(response: Response, request: Request, db=Depends(get_db)):
    clear_session(db, request.cookies.get(COOKIE, ''), response)
    return {'ok': True}


@router.get('/me', response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
