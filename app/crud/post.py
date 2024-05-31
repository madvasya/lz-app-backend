from datetime import datetime, timezone
from app.models import Post as PostDBModel
from fastapi import HTTPException
from sqlalchemy import asc, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.post import PostCommentCreate, PostReadSimple
from app.models import User as UserDBModel


async def get_posts_multi(
    db_session: AsyncSession,
    limit: int,
    offset: int,
    order_list: str,
) -> tuple[list[PostReadSimple], int]:
    count_stmt = select(func.count()).select_from(PostDBModel)
    select_stmt = select(PostDBModel).limit(limit).offset(offset)

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
    else:
        select_stmt = select_stmt.order_by(desc("created_on"))

    posts = (await db_session.scalars(select_stmt)).all()
    count = (await db_session.scalars(count_stmt)).one()
    return posts, count


async def get_post(db_session: AsyncSession, post_id: int):
    post = (
        await db_session.scalars(
            select(PostDBModel).where(
                PostDBModel.id == post_id
            )
        )
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

async def like_post(
    db_session: AsyncSession,
    post_id: int,
    user: UserDBModel
):
    post = await get_post(db_session, post_id)
    post.likes+=1
    return post.likes

async def dislike_post(
    db_session: AsyncSession,
    post_id: int,
    user: UserDBModel
):
    post = await get_post(db_session, post_id)
    post.dislikes+=1
    return post.dislikes

async def post_comment(
    db_session: AsyncSession,
    post_id: int,
    comment: PostCommentCreate,
    user: UserDBModel
):
    post = await get_post(db_session, post_id)
    return post.dislikes