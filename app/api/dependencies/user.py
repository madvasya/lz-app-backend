from typing import Annotated

from app import models
from app.api.dependencies.core import DBSessionDep
from app.crud.user import get_user_by_username, get_user_permissions
from app.schemas.auth import TokenData
from app.utils.auth import decode_jwt, oauth2_scheme
from fastapi import Depends, HTTPException, status
from jose import JWTError


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db_session: DBSessionDep
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db_session, token_data.username)
    if user is None:
        raise credentials_exception
    return user


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]


class UserHasPermission:
    def __init__(self, permission: str):
        self.permission = permission

    def __call__(self, current_user: CurrentUserDep) -> bool:
        if current_user.is_superadmin:
            return True
        user_permissions = get_user_permissions(current_user)
        if self.permission in user_permissions:
            return True
        raise HTTPException(status_code=403, detail="Not enough permissions")
