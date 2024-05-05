from datetime import datetime, timezone
from app.models import User as UserDBModel
from app.models import Role as RoleDBModel
from fastapi import HTTPException
from sqlalchemy import asc, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate
from app.schemas.user import UserUpdatePassword
from app.schemas.user import UserResetPassword
from app.utils.auth import get_password_hash, verify_password


async def get_user(db_session: AsyncSession, user_id: int):
    user = await db_session.get(UserDBModel, user_id)
    user = (
            await db_session.scalars(
                select(UserDBModel).where(
                    UserDBModel.id == user_id,
                )
            )
        ).first()
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User id={user_id} not found"
        )
    return user


async def get_user_by_username(db_session: AsyncSession, username: str):
    user = (
        await db_session.scalars(
            select(UserDBModel).where(UserDBModel.username == username)
        )
    ).first()
    return user


async def check_email(db_session: AsyncSession, email: str):
    user = (
        await db_session.scalars(
            select(UserDBModel).where(UserDBModel.email == email)
        )
    ).first()
    if user is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Email '{user.email}' is already registered",
        )


async def get_users_multi(
    db_session: AsyncSession,
    limit: int,
    offset: int,
    order_list: str,
) -> tuple[list[UserDBModel], int]:
    count_stmt = select(func.count()).select_from(UserDBModel)
    select_stmt = select(UserDBModel).limit(limit).offset(offset)

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

    users = (await db_session.scalars(select_stmt)).all()
    count = (await db_session.scalars(count_stmt)).one()
    return users, count


async def authenticate_user(
    db_session: AsyncSession, username: str, password: str
):
    user = await get_user_by_username(db_session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(
    db_session: AsyncSession, user: UserCreate
):
    db_user = await get_user_by_username(db_session, username=user.username)
    if db_user is not None:
        raise HTTPException(
            status_code=409, detail="Username already registered"
        )
    db_user = UserDBModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db_session.add(db_user)
    return db_user


async def update_user(
    db_session: AsyncSession,
    user_id: int,
    user_patch: UserUpdate,
):
    user = await get_user(db_session, user_id)
    if user.is_superadmin:
        raise HTTPException(status_code=403)
    if user_patch.email is not None:
        user.email = user_patch.email
    if user_patch.username is not None:
        duplicate_user = await get_user_by_username(
            db_session, user_patch.username
        )
        if duplicate_user and duplicate_user != user_id:
            raise HTTPException(
                status_code=409,
                detail=f"Username '{user_patch.username}' already registered",
            )
        user.username = user_patch.username
    if user_patch.full_name is not None:
        user.full_name = user_patch.full_name
    user.edited_on = datetime.now(timezone.utc)
    return user


async def update_user_password(
    db_session: AsyncSession,
    user_id: int,
    password_form: UserUpdatePassword,
):
    user = await get_user(db_session, user_id)
    if not verify_password(password_form.old_password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Old password is incorrect"
        )
    for session in user.sessions:
        await db_session.delete(session)
    user.hashed_password = get_password_hash(password_form.new_password)
    user.edited_on = datetime.now(timezone.utc)
    return user


# объединить с update_user_password в зависимости от типа password_form?
async def reset_user_password(
    db_session: AsyncSession,
    user_id: int,
    password_form: UserResetPassword,
):
    user = await get_user(db_session, user_id)
    for session in user.sessions:
        await db_session.delete(session)
    user.hashed_password = get_password_hash(password_form.new_password)
    user.edited_on = datetime.now(timezone.utc)
    return user


async def delete_user(db_session: AsyncSession, user_id: int):
    user_to_delete = await get_user(db_session, user_id)
    if user_to_delete.is_superadmin:
        raise HTTPException(
            status_code=403, detail="Admin user is protected from deletion"
        )
    await db_session.delete(user_to_delete)


async def assign_roles(
    db_session: AsyncSession,
    user_id: int,
    role_names: list[str],
):
    user = await get_user(db_session, user_id)
    for role_name in role_names:
        role = (
            await db_session.scalars(
                select(RoleDBModel).where(RoleDBModel.name == role_name)
            )
        ).first()
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role '{role_name}' not found"
            )
        if role in user.user_roles:
            raise HTTPException(
                status_code=409, detail=f"User already has '{role.name}' role"
            )
        user.user_roles.append(role)
    return user.user_roles


async def delete_roles(
    db_session: AsyncSession,
    user_id: int,
    role_names: list[str],
):
    user = await get_user(db_session, user_id)
    user.user_roles = [x for x in user.user_roles if x.name not in role_names]
    # ^ выглядит как сущий кошмар. поискать способ получше?
    return user.user_roles


def get_user_permissions(user: UserDBModel) -> list[str]:
    permissions = set()
    for role in user.user_roles:
        permissions.update(role.role_permissions)
    permissions_list = [x.permission_key for x in permissions]
    return permissions_list
