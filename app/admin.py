from sqladmin import Admin, ModelView

from app.database import engine
from app.main import app
from users.models import User

admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]


admin.add_view(UserAdmin)
