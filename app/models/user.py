import datetime
import uuid as uuid_pkg
from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Column, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.post import Post, PostComment
from app.models.rehearsal import Rehearsal


user_roles_table = Table(
    "lz_user_roles",
    Base.metadata,
    Column("role_id", ForeignKey("lz_roles.id"), primary_key=True),
    Column("user_id", ForeignKey("lz_users.id"), primary_key=True),
)


permission_in_role_table = Table(
    "lz_permission_in_role",
    Base.metadata,
    Column("role_id", ForeignKey("lz_roles.id"), primary_key=True),
    Column(
        "permission_id", ForeignKey("lz_permissions.id"), primary_key=True
    ),
)


class User(Base):
    __tablename__ = "lz_users"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    full_name: Mapped[str]
    hashed_password: Mapped[str]
    penalty_points: Mapped[int] = mapped_column(default=0)
    is_superadmin: Mapped[bool] = mapped_column(default=False)
    created_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )
    edited_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", lazy="selectin", cascade="delete, delete-orphan"
    )
    blocks: Mapped[list["UserBlock"]] = relationship(
        back_populates="user", lazy="selectin", cascade="delete, delete-orphan"
    )
    user_roles: Mapped[List["Role"]] = relationship(
        secondary=user_roles_table,
        back_populates="users_with_role",
        lazy="selectin",
    )
    rehearsals: Mapped[list["Rehearsal"]] = relationship(
        back_populates="user", lazy="selectin", cascade="delete, delete-orphan"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="user", lazy="selectin", cascade="delete, delete-orphan"
    )
    comments: Mapped[list["PostComment"]] = relationship(
        back_populates="user", lazy="selectin", cascade="delete, delete-orphan"
    )


class UserSession(Base):
    __tablename__ = "lz_sessions"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid_pkg.uuid4,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("lz_users.id"))
    user: Mapped["User"] = relationship(
        back_populates="sessions", lazy="selectin"
    )
    created_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )
    is_active: Mapped[bool] = mapped_column(default=True)


class UserBlock(Base):
    __tablename__ = "lz_blocks"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid_pkg.uuid4,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("lz_users.id"))
    user: Mapped["User"] = relationship(
        back_populates="blocks", lazy="selectin"
    )
    banned_on: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=func.CURRENT_TIMESTAMP()
    )
    banned_till: Mapped[datetime.datetime] = mapped_column(
        nullable=False
    )
    reason: Mapped[str]


class Role(Base):
    __tablename__ = "lz_roles"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]]

    role_permissions: Mapped[List["Permission"]] = relationship(
        secondary=permission_in_role_table,
        back_populates="permission_roles",
        lazy="selectin",
    )

    users_with_role: Mapped[List["User"]] = relationship(
        secondary=user_roles_table, back_populates="user_roles"
    )


class Permission(Base):
    __tablename__ = "lz_permissions"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    description: Mapped[str]
    permission_key: Mapped[str] = mapped_column(unique=True)

    permission_roles: Mapped[List["Role"]] = relationship(
        secondary=permission_in_role_table, back_populates="role_permissions"
    )
