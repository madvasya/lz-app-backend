from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserLogin
from app.schemas.auth import Token, TokenPair, RefreshToken
from app.api.dependencies.core import DBSessionDep
from app.crud.user import authenticate_user
from app.crud import session
from app.utils.auth import create_token

router = APIRouter()


@router.post("/token", include_in_schema=False)
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: DBSessionDep,
) -> Token:
    user = await authenticate_user(
        db_session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token(data={"sub": user.username}, type="access")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login")
async def login(login_data: UserLogin, db_session: DBSessionDep) -> TokenPair:
    user = await authenticate_user(
        db_session, login_data.username, login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_session = await session.create_user_session(db_session, user)
    await db_session.commit()
    access_token = create_token(data={"sub": user.username}, type="access")
    refresh_token = create_token(
        data={"sub": str(user_session.uuid)}, type="refresh"
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.delete("/logout")
async def logout(
    db_session: DBSessionDep, refresh_token: RefreshToken
) -> None:
    try:
        await session.delete_user_session(db_session, refresh_token)
        await db_session.commit()
    except KeyError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return None


@router.post("/refresh")
async def update_refresh_token(
    db_session: DBSessionDep, refresh_token: RefreshToken
) -> TokenPair:
    new_session = await session.update_user_session(db_session, refresh_token)
    if not new_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    await db_session.commit()
    access_token = create_token(
        data={"sub": new_session.user.username}, type="access"
    )
    refresh_token = create_token(
        data={"sub": str(new_session.uuid)}, type="refresh"
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
