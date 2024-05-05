from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPair(Token):
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None
