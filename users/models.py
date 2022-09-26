from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

from app.database import Base

class Roles:
    EMPLOYEE_ROLE = 'employee'


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    hashed_password = Column(String)
    salt = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    e_number = Column(Integer, unique=True, index=True, nullable=False)
    role = Column(String, nullable=True, default=Roles.EMPLOYEE_ROLE)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

    def __str__(self):
        return F"User: {self.e_number}"
