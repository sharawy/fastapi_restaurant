from typing import List, Union

from fastapi import HTTPException, Depends
from starlette import status

from users import get_current_active_user
from users.models import Roles
from users.schemas import UserSchema


class RoleChecker:
    def __init__(self, allowed_roles: List = []):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserSchema = Depends(get_current_active_user)):
        if user.is_admin:
            return
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Operation not permitted")


ADMIN_ROLE = RoleChecker()
EMPLOYEE_ROLE = RoleChecker([Roles.EMPLOYEE_ROLE])
