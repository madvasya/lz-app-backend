from fastapi import APIRouter, Query, Response
from app.crud.post import dislike_post, get_post, get_posts_multi, like_post
from app.schemas.post import PostComment, PostCommentCreate, PostRead, PostReadSimple
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep
from typing import Annotated
from typing import List

router = APIRouter()


@router.get("")
async def get_all_posts(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
    response: Response,
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
    order_list: str | None = None,
) -> List[PostReadSimple]:
    users, count = await get_posts_multi(
        db_session, limit, offset, order_list
    )
    response.headers["X-Total-Count"] = str(count)
    return users

@router.get("/{post_id}")
async def get_post_by_id(
    current_user: CurrentUserDep,
    post_id: int,
    db_session: DBSessionDep,
) -> PostRead:
    post = await get_post(
        db_session, post_id
    )
    return post

@router.patch("/{post_id}/like")
async def put_like_on_post(
    current_user: CurrentUserDep,
    post_id: int,
    db_session: DBSessionDep,
) -> int:
    likes = await like_post(
        db_session, post_id, current_user.id
    )
    await db_session.commit()
    return likes

@router.patch("/{post_id}/dislike")
async def put_dislike_on_post(
    current_user: CurrentUserDep,
    post_id: int,
    db_session: DBSessionDep,
) -> int:
    dislikes = await dislike_post(
        db_session, post_id, current_user.id
    )
    await db_session.commit()
    return dislikes

# @router.post("/{post_id}/comment")
# async def write_comment_to_post(
#     current_user: CurrentUserDep,
#     post_id: int,
#     comment: PostCommentCreate,
#     db_session: DBSessionDep,
# ) -> PostComment:
#     likes = await post_comment(
#         db_session, post_id, current_user.id
#     )
#     await db_session.commit()
#     return likes