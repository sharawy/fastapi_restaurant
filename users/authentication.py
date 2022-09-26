from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import HTTPException, Depends
from fastapi_redis_cache import cache, FastApiRedisCache
from fastapi_redis_cache.util import deserialize_json
from jose import jwt
from jsonschema import ValidationError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.core.config import settings
from app.dependencies import oauth2_scheme, get_db
from app.utils import get_from_cache, add_to_cache
from .schemas import UserPasswordUpdate, JWTMeta, JWTCreds, JWTPayload, UserSchema, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authenticate():
    def create_salt_and_hashed_password(self, *, plaintext_password: str) -> UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt)
        return UserPasswordUpdate(salt=salt, password=hashed_password)

    @staticmethod
    def generate_salt() -> str:
        return bcrypt.gensalt().decode()

    @staticmethod
    def hash_password(*, password: str, salt: str) -> str:
        return pwd_context.hash(password + salt)

    @staticmethod
    def verify_password(*, password: str, salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(password + salt, hashed_pw)

    @staticmethod
    def create_access_token_for_user(
            *,
            user: UserSchema,
            secret_key: str = str(settings.SECRET_KEY),
            audience: str = settings.JWT_AUDIENCE,
            expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> Optional[str]:
        if not user or not isinstance(user, UserSchema):
            return None
        jwt_meta = JWTMeta(
            aud=audience,
            iat=datetime.timestamp(datetime.now()),
            exp=datetime.timestamp(datetime.now() + timedelta(minutes=expires_in)),
        )
        jwt_creds = JWTCreds(sub=user.id, e_number=user.e_number)
        token_payload = JWTPayload(
            **jwt_meta.dict(),
            **jwt_creds.dict(),
        )
        return jwt.encode(
            token_payload.dict(), secret_key, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def get_e_number_from_token(*,
                                token: str,
                                secret_key: str = str(settings.SECRET_KEY)) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, str(secret_key),
                                       audience=settings.JWT_AUDIENCE,
                                       algorithms=[settings.JWT_ALGORITHM])
            payload = JWTPayload(**decoded_token)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.e_number

    def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserSchema:

        from users.crud import get_user_by_e_number

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            e_number = self.get_e_number_from_token(token=token)
            token_data = TokenData(e_number=e_number)
        except jwt.JWTError:
            raise credentials_exception

        in_cache = get_from_cache(str(token_data.e_number))
        if not in_cache:
            user = get_user_by_e_number(e_number=token_data.e_number, db=db)
            add_to_cache(str(token_data.e_number), user.dict(), 3600)
        else:
            user = UserSchema(**in_cache)

        if user is None:
            raise credentials_exception
        return user


def get_current_active_user(current_user: UserSchema = Depends(Authenticate().get_current_user)) -> UserSchema:
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user


def check_if_user_is_admin(current_user: UserSchema = Depends(get_current_active_user)) -> UserSchema:
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail="You have not enough privileges")
    return current_user
