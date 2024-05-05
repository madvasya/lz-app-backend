from fastapi import APIRouter
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep
from app.schemas.permission import Permission
from app.crud.permission import get_permissions
from app.crud.user import get_user_permissions

router = APIRouter()


@router.get("")
async def get_all_permissions(
    db_session: DBSessionDep, _: CurrentUserDep
) -> list[Permission]:
    permissions = await get_permissions(db_session)
    return permissions


@router.get("/me")
async def get_my_permissions(
    db_session: DBSessionDep, current_user: CurrentUserDep
) -> list[str]:
    if current_user.is_superadmin:
        permissions = await get_permissions(db_session)
        permissions = [x.permission_key for x in permissions]
    else:
        permissions = get_user_permissions(user=current_user)
    return permissions
