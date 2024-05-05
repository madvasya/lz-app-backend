import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, func
from app.database import Base

class Post(Base):
    __tablename__ = "lz_posts"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    title: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()
    likes: Mapped[str] = mapped_column(default=0)
    dislikes: Mapped[str] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("lz_users.id"))
    user: Mapped["User"] = relationship(
        back_populates="posts", lazy="selectin"
    )
    created_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )
    edited_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )
    post_comments: Mapped[List["PostComment"]] = relationship(
        back_populates="post",
        lazy="selectin",
        cascade="delete, delete-orphan"
    )

class PostComment(Base):
    __tablename__ = "lz_post_comments"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    text: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("lz_users.id"))
    user: Mapped["User"] = relationship(
        back_populates="comments", lazy="selectin"
    )
    post_id: Mapped[int] = mapped_column(ForeignKey("lz_posts.id"))
    post: Mapped["Post"] = relationship(
        back_populates="post_comments", lazy="selectin"
    )
    start_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    band_name: Mapped[str] = mapped_column()