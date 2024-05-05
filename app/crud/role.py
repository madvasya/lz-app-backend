from fastapi import HTTPException
from app.models import Role as RoleDBModel, Permission as PermissionDBModel
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.role import RoleCreate, RoleUpdate
from app.models.user import User as UserDBModel


async def get_role(db_session: AsyncSession, role_id: int):
    role = (
        await db_session.scalars(
            select(RoleDBModel).where(
                RoleDBModel.id == role_id
            )
        )
    ).first()
    return role


async def get_role_by_name(
    db_session: AsyncSession, role_name: str
):
    role = (
        await db_session.scalars(
            select(RoleDBModel)
            .where(RoleDBModel.name == role_name)
        )
    ).first()
    return role


async def get_roles_multi(
    db_session: AsyncSession,
    limit: int,
    offset: int,
    order_list: str,
):
    select_stmt = select(RoleDBModel)
    count_stmt = select(func.count()).select_from(RoleDBModel)
    if order_list is not None:
        direction, sort_label = order_list.split("_", maxsplit=1)
        if direction == "asc":
            select_stmt = select_stmt.order_by(asc(sort_label))
        elif direction == "desc":
            select_stmt = select_stmt.order_by(desc(sort_label))
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unexpectable order prefix {direction}",
            )

    roles = (
        await db_session.scalars(select_stmt.limit(limit).offset(offset))
    ).all()
    count = (await db_session.scalars(count_stmt)).one()
    return roles, count


async def create_role(
    db_session: AsyncSession, role: RoleCreate
):
    duplicate_role = await get_role_by_name(db_session, role.name)
    if duplicate_role:
        raise HTTPException(
            status_code=409, detail=f"Role '{role.name}' already exists"
        )
    db_role = RoleDBModel(
        name=role.name, description=role.description
    )
    db_session.add(db_role)
    return db_role


async def update_role(
    db_session: AsyncSession,
    role_id: int,
    role_patch: RoleUpdate,
):
    role = await get_role(db_session, role_id)
    if not role:
        return role
    if role_patch.name is not None:
        duplicate_role = await get_role_by_name(
            db_session, role_patch.name
        )
        if duplicate_role and duplicate_role.id != role_id:
            raise HTTPException(
                status_code=409,
                detail=f"Role '{role_patch.name}' already exists",
            )
        role.name = role_patch.name
    if role_patch.description is not None:
        role.description = role_patch.description
    return role


async def delete_role(db_session: AsyncSession, role_id: int):
    role_to_delete = await get_role(db_session, role_id)
    if not role_to_delete:
        raise KeyError("Role not found")
    await db_session.delete(role_to_delete)


async def assign_permissions(
    db_session: AsyncSession,
    role_id: int,
    permission_names: list[str],
):
    role = await get_role(db_session, role_id)
    if not role:
        raise KeyError("Role not found")
    for permission_key in permission_names:
        permission = (
            await db_session.scalars(
                select(PermissionDBModel).where(
                    PermissionDBModel.permission_key == permission_key
                )
            )
        ).first()
        if not permission:
            raise ValueError(f"Permission '{permission_key}' not found")
        if permission in role.role_permissions:
            raise ValueError(
                f"Permission '{permission.permission_key}' is already in role"
            )
        role.role_permissions.append(permission)
    return role.role_permissions


async def delete_permissions(
    db_session: AsyncSession,
    role_id: int,
    permission_names: list[str],
):
    role = await get_role(db_session, role_id)
    if not role:
        raise KeyError("Role not found")
    role.role_permissions = [
        x
        for x in role.role_permissions
        if x.permission_key not in permission_names
    ]
    return role.role_permissions


async def get_permissions(
    db_session: AsyncSession, role_id: int
):
    role = await get_role(db_session, role_id)
    if not role:
        raise KeyError("Role not found")
    return role.role_permissions
