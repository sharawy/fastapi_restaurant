from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.dependencies import get_db
from users import schemas, auth_service, get_current_active_user
from users.crud import create_user, get_user_by_e_number
from users.roles import ADMIN_ROLE
from users.schemas import UserCreate, AccessToken

router = APIRouter(prefix="/v1/users",
                   tags=["users"],
                   )


@router.post("/", response_model=schemas.UserPublic, status_code=status.HTTP_201_CREATED)
def user_create(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_e_number(user.e_number, db):
        raise HTTPException(status_code=400, detail="Employee number already exists")
    return create_user(user, db)


@router.post(
    '/login',
    tags=["user login"],
    description="Log in the User",
    response_model=schemas.UserPublic
)
def user_login(user: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.UserPublic:
    found_user = get_user_by_e_number(e_number=user.e_number, db=db)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee number or password not valid.",
        )
    if auth_service.verify_password(password=user.password, salt=found_user.salt, hashed_pw=found_user.hashed_password):
        # If the provided password is valid one then we are going to create an access token
        token = auth_service.create_access_token_for_user(user=found_user)
        access_token = AccessToken(access_token=token, token_type='bearer')
        return schemas.UserPublic(**found_user.dict(), access_token=access_token)


@router.get(
    "/info",
    tags=["get current logged in user"],
    description="Get current logged in user",
    response_model=schemas.UserPublic,
)
def get_me(db: Session = Depends(get_db),
           current_user: schemas.UserSchema = Depends(get_current_active_user)) -> schemas.UserPublic:
    return current_user
