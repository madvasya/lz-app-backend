from pydantic import BaseModel, ConfigDict
from app.schemas.permission import Permission
from app.utils.types import NameStr, DescriptionStr


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: NameStr
    description: DescriptionStr


class RoleCreate(BaseModel):
    name: NameStr
    description: DescriptionStr | None = None


class RoleUpdate(BaseModel):
    name: NameStr | None = None
    description: DescriptionStr | None = None


class RoleInDB(Role):
    pass


class RoleRead(RoleInDB):
    role_permissions: list[Permission]


class RolePermissions(BaseModel):
    role_permissions: list[Permission]
