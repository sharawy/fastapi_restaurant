import pytest

from users import auth_service
from users.schemas import UserSchema, UserCreate


@pytest.fixture(scope="class")
def auth_obj():
    return auth_service


@pytest.yield_fixture
def user_to_create():
    yield UserCreate(
        e_number=1000,
        password="testclientpassword"
    )


@pytest.fixture(scope="class")
def dummy_user(auth_obj) -> UserSchema:
    new_user = UserCreate(
        e_number=1000,
        password="dummyuserswesomepass",
    )
    new_password = auth_obj.create_salt_and_hashed_password(plaintext_password=new_user.password)
    new_user_params = new_user.copy( \
        update={'salt': new_password.salt, 'hashed_password': new_password.password, 'id': 2, 'is_active': True,
                'is_admin': False})
    return UserSchema(**new_user_params.dict())
