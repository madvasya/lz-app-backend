from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.JWT_PRIVATE_KEY, algorithms=["HS256"])


def create_token(
    data: dict, type: str, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = () + expires_delta
    else:
        if type == "access":
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRES_IN
            )
        elif type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRES_IN
            )
        else:
            raise Exception(f"could not create '{type}' token")
    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_PRIVATE_KEY, algorithm="HS256"
    )
    return encoded_jwt
