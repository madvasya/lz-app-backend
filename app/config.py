from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    API_STR: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    @computed_field
    def db_config(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int

    FRONTEND_ORIGIN: str


@cache
def get_settings():
    return Settings()
