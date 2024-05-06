from fastapi import HTTPException
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.rehearsal import RehearsalCreate
from app.models import Rehearsal as RehearsalDBModel, RehearsalParticipant as RehearsalParticipantDBModel
from app.models import User as UserDBModel

async def get_rehearsal(db_session: AsyncSession, rehearsal_id: int):
    rehearsal = (
        await db_session.scalars(
            select(RehearsalDBModel).where(
                RehearsalDBModel.id == rehearsal_id
            )
        )
    ).first()
    if not rehearsal:
        raise HTTPException(status_code=404, detail="Rehearsal not found")
    return rehearsal

async def get_rehearsals_multi(
    db_session: AsyncSession,
    limit: int,
    offset: int,
    order_list: str,
):
    select_stmt = select(RehearsalDBModel)
    count_stmt = select(func.count()).select_from(RehearsalDBModel)
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

async def create_rehearsal(
    db_session: AsyncSession, rehearsal: RehearsalCreate, user: UserDBModel
):
    db_rehearsal = RehearsalDBModel(
        user_id=user.id,
        start_time=rehearsal.start_time,
        duration=rehearsal.duration,
        band_name=rehearsal.band_name,
    )
    db_session.add(db_rehearsal)
    await db_session.flush([db_rehearsal])
    participants_for_db: list[RehearsalParticipantDBModel] = []
    for p in rehearsal.participants:
        participant = RehearsalParticipantDBModel(
            surname=p,
            rehearsal=db_rehearsal
            )
        db_session.add(participant)
        participants_for_db.append(participant)

    await db_session.flush(participants_for_db)
    return db_rehearsal


async def delete_rehearsal(db_session: AsyncSession, rehearsal_id: int):
    rehearsal_to_delete = await get_rehearsal(db_session, rehearsal_id)
    await db_session.delete(rehearsal_to_delete)
