from pydantic import BaseModel, EmailStr, ConfigDict, Field, computed_field
from app.utils.types import UserNameStr, PasswordStr, FullNameStr
from datetime import datetime


class RehearsalParticipant(BaseModel):
    surname: str
    rehearsal_id: int


class RehearsalCreate(BaseModel):
    participants: list[str]
    start_time: datetime
    duration: int
    band_name: str


class RehearsalRead(BaseModel):
    id: int
    user_id: int
    rehearsal_participants: list[RehearsalParticipant]
    band_name: str
    start_time: datetime
    duration: int