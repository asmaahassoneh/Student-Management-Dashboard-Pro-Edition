from app.extensions import db
from app.models.user import User
from app.utils.validators import normalize_email, normalize_text


def get_all_users(search=None):
    query = User.query.order_by(User.username.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.role.ilike(f"%{search}%"))
        )

    return query.all()


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


def create_user(data):
    user = User(
        username=normalize_text(data["username"]),
        email=normalize_email(data["email"]),
        role=data.get("role", User.ROLE_STUDENT),
        profile_picture=data.get("profile_picture"),
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()
    return user


def update_user(user, data):
    if "username" in data:
        user.username = normalize_text(data["username"])

    if "email" in data:
        user.email = normalize_email(data["email"])

    if "role" in data:
        user.role = data["role"]

    if "profile_picture" in data:
        user.profile_picture = data["profile_picture"]

    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()
    return user


def delete_user(user):
    db.session.delete(user)
    db.session.commit()
