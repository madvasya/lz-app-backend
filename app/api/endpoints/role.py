from fastapi import APIRouter, Query, HTTPException, Depends, Response
from typing import Annotated, List
from app.schemas.role import RoleRead, RoleCreate, RoleUpdate
from app.schemas.permission import Permission
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep, UserHasPermission
from app.crud.role import (
    get_roles_multi,
    get_role,
    create_role,
    update_role,
    delete_role,
    assign_permissions,
    delete_permissions,
    get_permissions,
)

router = APIRouter()


@router.get("")
async def get_all_roles(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    response: Response,
    _: Annotated[bool, Depends(UserHasPermission("role_read"))],
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
    order_list: str | None = None,
) -> List[RoleRead]:
    roles, count = await get_roles_multi(
        db_session, limit, offset, order_list
    )
    response.headers["X-Total-Count"] = str(count)
    return roles


@router.post("")
async def add_role(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    new_role: RoleCreate,
    _: Annotated[bool, Depends(UserHasPermission("role_update"))],
) -> RoleRead:
    role = await create_role(db_session, new_role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@router.get("/{role_id}")
async def get_role_info(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    _: Annotated[bool, Depends(UserHasPermission("role_read"))],
) -> RoleRead:
    role = await get_role(db_session, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/{role_id}")
async def edit_role_info(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    patch_fields: RoleUpdate,
    _: Annotated[bool, Depends(UserHasPermission("role_update"))],
) -> RoleRead:
    role = await update_role(
        db_session, role_id, patch_fields
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await db_session.commit()
    return role


@router.delete("/{role_id}")
async def remove_role(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    _: Annotated[bool, Depends(UserHasPermission("role_update"))],
) -> None:
    try:
        await delete_role(db_session, role_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Role not found")
    await db_session.commit()
    return "role deleted"


@router.post("/{role_id}/permissions")
async def assign_permissions_to_role(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    permission_list: Annotated[List[str], Query()],
    _: Annotated[bool, Depends(UserHasPermission("role_update"))],
) -> list[Permission]:
    try:
        result = await assign_permissions(
            db_session, role_id, permission_list
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await db_session.commit()
    return result


@router.delete("/{role_id}/permissions")
async def unassign_permissions_from_role(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    permission_list: Annotated[List[str], Query()],
    _: Annotated[bool, Depends(UserHasPermission("role_update"))],
) -> list[Permission]:
    try:
        result = await delete_permissions(
            db_session, role_id, permission_list
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    await db_session.commit()
    return result


@router.get("/{role_id}/permissions")
async def get_permissions_in_role(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    role_id: int,
    _: Annotated[bool, Depends(UserHasPermission("role_read"))],
) -> list[Permission]:
    try:
        permissions = await get_permissions(
            db_session=db_session,
            role_id=role_id,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Role not found")
    await db_session.commit()
    return permissions
