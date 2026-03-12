from datetime import datetime, timedelta, timezone
import uuid
from fastapi import APIRouter, Depends, Cookie, Header, Response
from typing import Annotated
import jwt
from jwt import ExpiredSignatureError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException,status
from app.models import User,Task
from app.core.database import get_db
from app.schemas import UserSchema, UserCreate, UserResponse,Tokens,RefreshRequest
from app.models import User, AuthSessions
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import get_current_user

from app.api.dependencies import (
    get_current_active_user,
    CurrentUser,
    authenticate_user,
)
import shutil
from pwdlib import PasswordHash



router = APIRouter(
    tags= ["Users"]

)
password_hash = PasswordHash.recommended()



def get_password_hash(password):
    return password_hash.hash(password)



@router.post("/users", response_model=UserResponse)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)):

    exists_username = db.query(User).filter(User.username == user.username).first()
    if exists_username:
        raise HTTPException(status_code=409, detail="This username is not available")

    new_password = get_password_hash(password=user.password)
    new_user = User(name=user.name, username= user.username, hashed_password=new_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.post("/token")
async def get_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # ACCESS
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "type": "access"},
        expires_delta=access_token_expires
    )

    # REFRESH
    jti = str(uuid.uuid4())
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXP_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "type": "refresh", "jti": jti},
        expires_delta=refresh_token_expires
    )

    db.query(AuthSessions).filter(AuthSessions.user_id==user.id, AuthSessions.revoked==False).update({"revoked": True})
    new_session = AuthSessions(
        user_id=user.id,
        jti=jti,
        revoked=False,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)


    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # xss sec.
        secure=False,    # LOCAL FALSE
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, #LOCAL FALSE
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXP_DAYS*24*60*60
    )

    csrf_token = str(uuid.uuid4())
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  #JS can read and send X-CSRF-Token
        secure=False, #LOCAL FALSE
        samesite="lax"
    )

    return {"message": "Logged in", "csrf_token": csrf_token}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    db: Session = Depends(get_db),
    csrf_token_header: str = Header(None, alias="X-CSRF-Token"),
    refresh_token: str = Cookie(None),
):

    csrf_token_cookie = response.cookies.get("csrf_token")
    if csrf_token_header != csrf_token_cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")

    payload = jwt.decode(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
    if payload["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    session = db.query(AuthSessions).filter(AuthSessions.jti==payload["jti"], AuthSessions.revoked==False).first()
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session invalid")

    session.revoked = True


    new_jti = str(uuid.uuid4())
    new_refresh_token = create_refresh_token(
        data={"sub": payload["sub"], "type":"refresh", "jti": new_jti},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXP_DAYS)
    )
    new_session = AuthSessions(
        user_id=session.user_id,
        jti=new_jti,
        revoked=False,
        expires_at=datetime.now(timezone.utc)+timedelta(days=settings.REFRESH_TOKEN_EXP_DAYS)
    )

    access_token = create_access_token(
        data={"sub": payload["sub"], "type":"access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)


    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # локально False
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # локально False
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXP_DAYS * 24 * 60 * 60
    )

@router.get("/users/me")
async def get_users_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username}