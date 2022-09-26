import string
from datetime import datetime, timedelta
from typing import Optional

from pydantic import validator, constr, Field

from app.core.config import settings
from app.dependencies import get_db
from app.schemas import CoreModel, IDModelMixin, DateTimeModelMixin


def validate_username(username: str) -> str:
    allowed = string.ascii_letters + string.digits + "-" + "_"
    assert all(char in allowed for char in username), "Invalid characters in username."
    assert len(username) >= 3, "Username must be 3 characters or more."
    return username


class UserBase(CoreModel):
    e_number: int = Field(
        title='employee number',
        gt=999,
        le=9999,
    )
    is_active: bool
    role: Optional[str]
    is_admin: bool


class UserCreate(CoreModel, DateTimeModelMixin):
    e_number: int = Field(
        title='employee number',
        gt=999,
        le=9999,
    )
    password: constr(min_length=6, max_length=100)


class UserPasswordUpdate(CoreModel):
    """
    Users can change their password
    """
    password: constr(min_length=6, max_length=100)
    salt: str

    class Config:
        orm_mode = True


class JWTMeta(CoreModel):
    iss: str = "azepug.az"
    aud: str = settings.JWT_AUDIENCE
    iat: float = datetime.timestamp(datetime.now())
    exp: float = datetime.timestamp(datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


class JWTCreds(CoreModel):
    """How we'll identify users"""
    sub: str
    e_number: int


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """
    pass


class AccessToken(CoreModel):
    access_token: str
    token_type: str


class UserSchema(IDModelMixin, DateTimeModelMixin, UserBase):
    salt: Optional[str]
    hashed_password: Optional[str]

    class Config:
        orm_mode = True


class UserLogin(CoreModel):
    """
    username and password are required for logging in the user
    """
    e_number: int
    password: constr(min_length=6, max_length=100)



class UserPublic(DateTimeModelMixin, UserBase):
    access_token: Optional[AccessToken]

    class Config:
        orm_mode = True


class TokenData(CoreModel):
    e_number: Optional[int] = None
