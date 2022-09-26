
from sqlalchemy.orm import Session

from users import auth_service, models
from users.schemas import UserCreate, UserSchema


def create_user(new_user: UserCreate, db: Session) -> UserSchema:
    # This is a UserPasswordUpdate
    new_password = auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
    db_item = models.User(e_number=new_user.e_number, hashed_password=new_password.password, salt=new_password.salt,
                          created_at=new_user.created_at, updated_at=new_user.updated_at)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_by_e_number(e_number: int, db: Session) -> UserSchema:
    user = db.query(models.User).filter_by(e_number=e_number).first()
    if user:
        return UserSchema.from_orm(user)
