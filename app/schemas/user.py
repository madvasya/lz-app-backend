from pydantic import BaseModel, EmailStr, ConfigDict, Field, computed_field
from app.utils.types import UserNameStr, PasswordStr, FullNameStr
from datetime import datetime
from app.schemas.role import RoleRead


class UserLogin(BaseModel):
    username: UserNameStr
    password: PasswordStr


class UserCreate(UserLogin):
    email: EmailStr | None = None
    full_name: FullNameStr | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: UserNameStr
    full_name: FullNameStr
    email: EmailStr
    created_on: datetime


class UserRead(User):
    user_roles: list[RoleRead] = Field(exclude=True)
    edited_on: datetime
    penalty_points: int

    @computed_field
    @property
    def roles(self) -> list[str]:
        return [role.name for role in self.user_roles]

    @computed_field
    @property
    def permissions(self) -> set[str]:
        permission_set = set()
        for role in self.user_roles:
            permission_set.update(
                [p.permission_key for p in role.role_permissions]
            )
        return permission_set


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: PasswordStr


class UserResetPassword(BaseModel):
    new_password: PasswordStr


class UserUpdate(BaseModel):
    username: UserNameStr | None = None
    email: EmailStr | None = None
    full_name: FullNameStr | None = None


class UserInDB(User):
    hashed_password: str
    is_admin: bool
    is_superadmin: bool
    edited_on: datetime


class UserSession(User):
    session_uuid: str

class UserBlock(BaseModel):
    id: int
    banned_on: datetime
    banned_till: datetime
    reason: str