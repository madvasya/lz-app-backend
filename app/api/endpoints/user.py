from fastapi import APIRouter, HTTPException, Query, Depends, Response
from app.crud.rehearsal import get_user_rehearsals
from app.schemas.rehearsal import RehearsalRead
from app.schemas.user import UserUpdatePassword, UserUpdate
from app.schemas.user import UserRead, UserCreate, UserResetPassword
from app.schemas.role import Role
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep, UserHasPermission
from app.crud.user import (
    update_user,
    update_user_password,
    create_user,
    delete_user,
    get_user_by_username,
    get_user,
    get_users_multi,
    assign_roles,
    reset_user_password,
    delete_roles,
    check_email,
)
from typing import Annotated
from typing import List

router = APIRouter()


@router.get("/me")
async def get_user_info_me(current_user: CurrentUserDep) -> UserRead:
    return current_user


@router.put("/me/password")
async def change_password_me(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    password_form: UserUpdatePassword,
) -> UserRead:
    if current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Don't shoot yourself")
    result = await update_user_password(
        db_session, current_user.id, password_form
    )
    await db_session.commit()
    return result


@router.patch("/me")
async def edit_user_me(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    new_fields: UserUpdate,
) -> UserRead:
    await update_user(
        db_session, current_user.id, new_fields
    )
    await db_session.commit()
    return current_user


@router.post("")
async def add_new_user(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
    user_data: UserCreate,
) -> UserRead:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not an admin")
    db_user = await get_user_by_username(
        db_session, username=user_data.username
    )
    if db_user is not None:
        raise HTTPException(
            status_code=409, detail="Username already registered"
        )
    await check_email(db_session, email=user_data.email)
    new_user = await create_user(
        db_session, user_data
    )
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user


@router.get("")
async def get_all_users(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
    _: Annotated[bool, Depends(UserHasPermission("user_read"))],
    response: Response,
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
    order_list: str | None = None,
) -> List[UserRead]:
    users, count = await get_users_multi(
        db_session, limit, offset, order_list
    )
    response.headers["X-Total-Count"] = str(count)
    return users


@router.get("/{user_id}")
async def get_user_info_by_id(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    user_id: int,
    _: Annotated[bool, Depends(UserHasPermission("user_read"))],
) -> UserRead:
    result = await get_user(db_session, user_id)
    return result


@router.delete("/{user_id}")
async def remove_user(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
    user_id: int,
    _: Annotated[bool, Depends(UserHasPermission("user_update"))],
):
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Don't shoot yourself")
    await delete_user(db_session, user_id)
    await db_session.commit()
    return "user deleted"


@router.patch("/{user_id}")
async def edit_user(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    user_id: int,
    new_fields: UserUpdate,
    _: Annotated[bool, Depends(UserHasPermission("user_update"))],
) -> UserRead:
    patched_user = await update_user(
        db_session, user_id, new_fields
    )
    await db_session.commit()
    return patched_user


@router.put("/{user_id}/password")
async def change_password_for_user(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    user_id: int,
    password: UserResetPassword,
    _: Annotated[bool, Depends(UserHasPermission("user_update"))],
) -> UserRead:
    if not current_user.is_superadmin or user_id == current_user.id:
        raise HTTPException(status_code=403)
    result = await reset_user_password(
        db_session, user_id, password, 
    )
    await db_session.commit()
    return result


@router.post("/{user_id}/roles")
async def assign_roles_to_user(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    user_id: int,
    role_list: Annotated[List[str], Query()],
    _: Annotated[bool, Depends(UserHasPermission("user_update"))],
) -> List[Role]:
    result = await assign_roles(
        db_session, user_id, role_list 
    )
    await db_session.commit()
    return result


@router.delete("/{user_id}/roles")
async def unassign_roles_from_user(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    user_id: int,
    role_list: Annotated[List[str], Query()],
    _: Annotated[bool, Depends(UserHasPermission("user_update"))],
) -> List[Role]:
    try:
        result = await delete_roles(
            db_session, user_id, role_list
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    await db_session.commit()
    return result


@router.get("/{user_id}/roles")
async def get_all_user_roles(
    db_session: DBSessionDep,
    user_id: int,
    current_user: CurrentUserDep,
    _: Annotated[bool, Depends(UserHasPermission("user_read"))],
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
) -> List[Role]:
    try:
        end = limit + offset
    except TypeError:
        end = limit
    user = await get_user(db_session, user_id)
    return user.user_roles[offset:end]


@router.get("/me/rehearsals")
async def get_rehearsals_my(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    archive: bool,
    response: Response,
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
) -> List[RehearsalRead]:
    rehearsals, count = await get_user_rehearsals(
        db_session, current_user.id, archive, limit, offset, 
    )
    response.headers["X-Total-Count"] = str(count)
    return rehearsals
