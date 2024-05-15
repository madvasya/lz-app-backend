from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends, Response
from typing import Annotated, List
from app.schemas.rehearsal import RehearsalRead, RehearsalCreate
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep, UserHasPermission
from app.crud.rehearsal import (
    get_rehearsals_multi,
    get_rehearsal,
    create_rehearsal,
 #   update_rehearsal,
    delete_rehearsal,
)

router = APIRouter()


@router.get("")
async def get_all_rehearsals(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    response: Response,
    #_: Annotated[bool, Depends(UserHasPermission("rehearsal_read"))],
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
    filter_from: datetime | None = None,
    filter_to: datetime | None = None
) -> List[RehearsalRead]:
    rehearsals, count = await get_rehearsals_multi(
        db_session, limit, offset, filter_from, filter_to
    )
    response.headers["X-Total-Count"] = str(count)
    return rehearsals


@router.post("")
async def add_rehearsal(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    new_rehearsal: RehearsalCreate,
    #_: Annotated[bool, Depends(UserHasPermission("rehearsal_update"))],
) -> RehearsalRead:
    rehearsal = await create_rehearsal(db_session, new_rehearsal, current_user)
    await db_session.commit()
    await db_session.refresh(rehearsal)
    return rehearsal


@router.get("/{rehearsal_id}")
async def get_rehearsal_info(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    rehearsal_id: int,
    #_: Annotated[bool, Depends(UserHasPermission("rehearsal_read"))],
) -> RehearsalRead:
    rehearsal = await get_rehearsal(db_session, rehearsal_id)
    return rehearsal


# @router.patch("/{rehearsal_id}")
# async def edit_rehearsal_info(
#     db_session: DBSessionDep,
#     current_user: CurrentUserDep,
#     rehearsal_id: int,
#     patch_fields: RehearsalUpdate,
#     #_: Annotated[bool, Depends(UserHasPermission("rehearsal_update"))],
# ) -> RehearsalRead:
#     rehearsal = await update_rehearsal(
#         db_session, rehearsal_id, patch_fields
#     )
#     if not rehearsal:
#         raise HTTPException(status_code=404, detail="Rehearsal not found")
#     await db_session.commit()
#     return rehearsal


@router.delete("/{rehearsal_id}")
async def remove_rehearsal(
    db_session: DBSessionDep,
    current_user: CurrentUserDep,
    rehearsal_id: int,
    #_: Annotated[bool, Depends(UserHasPermission("rehearsal_update"))],
) -> None:
    await delete_rehearsal(db_session, rehearsal_id)
    await db_session.commit()
    return "rehearsal deleted"