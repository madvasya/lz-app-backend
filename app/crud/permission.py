from app.models import Permission as PermissionDBModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_permissions(db_session: AsyncSession):
    permissions = (await db_session.scalars(select(PermissionDBModel))).all()
    return permissions
