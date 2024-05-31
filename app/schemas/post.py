from pydantic import BaseModel
from app.schemas.user import User
from datetime import datetime


class PostReadSimple(BaseModel):
    id: int
    user_id: int
    user: User
    title: str
    text: str
    likes: int
    dislikes: int
    created_on: datetime


class PostCreate(BaseModel):
    participants: list[str]
    start_time: datetime
    duration: int
    band_name: str


class PostComment(BaseModel):
    id: int
    text: str
    user: User
    created_on: datetime

class PostCommentCreate(BaseModel):
    text: str

class PostRead(BaseModel):
    id: int
    user_id: int
    user: User
    title: str
    text: str
    likes: int
    dislikes: int
    created_on: datetime
    post_comments: list[PostComment]
