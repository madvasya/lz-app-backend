from app.models import User as UserDBModel
from app.models import UserSession as UserSessionDBModel
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RefreshToken
from app.utils.auth import decode_jwt
from jose import JWTError
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def create_user_session(db_session: AsyncSession, user: UserDBModel):
    session = UserSessionDBModel(user=user)
    db_session.add(session)
    return session


async def delete_user_session(
    db_session: AsyncSession, refresh_token: RefreshToken
):
    try:
        payload = jwt.decode(
            token=refresh_token.refresh_token,
            key=settings.JWT_PRIVATE_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
    except JWTError:
        raise credentials_exception
    session_uuid = payload.get("sub")
    if session_uuid is None:
        raise credentials_exception
    session = (
        await db_session.scalars(
            select(UserSessionDBModel).where(
                UserSessionDBModel.uuid == session_uuid
            )
        )
    ).first()
    if not session:
        raise credentials_exception
    await db_session.delete(session)


async def update_user_session(
    db_session: AsyncSession, refresh_token: RefreshToken
):
    try:
        payload = decode_jwt(token=refresh_token.refresh_token)
    except JWTError:
        raise credentials_exception
    session_uuid = payload.get("sub")
    if session_uuid is None:
        return session_uuid
    session = await db_session.get(UserSessionDBModel, session_uuid)
    if not session:
        return session
    user = session.user
    await db_session.delete(session)
    new_session = await create_user_session(db_session, user)
    return new_session
