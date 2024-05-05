import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.database import Base

class Rehearsal(Base):
    __tablename__ = "lz_rehearsals"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("lz_users.id"))
    user: Mapped["User"] = relationship(
        back_populates="rehearsals", lazy="selectin"
    )
    start_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    band_name: Mapped[str] = mapped_column()
    rehearsal_participants: Mapped[List["RehearsalParticipant"]] = relationship(
        back_populates="rehearsal",
        lazy="selectin",
        cascade="delete, delete-orphan"
    )

class RehearsalParticipant(Base):
    __tablename__ = "lz_rehearsal_participants"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    rehearsal_id: Mapped[int] = mapped_column(ForeignKey("lz_rehearsals.id"))
    rehearsal: Mapped["Rehearsal"] = relationship(
        back_populates="rehearsal_participants", lazy="selectin"
    )
    start_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    band_name: Mapped[str] = mapped_column()