from pydantic import BaseModel


class Permission(BaseModel):
    permission_key: str
    description: str
