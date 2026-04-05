from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    ROLE_ADMIN = "admin"
    ROLE_INSTRUCTOR = "instructor"
    ROLE_STUDENT = "student"
    ROLES = [ROLE_ADMIN, ROLE_INSTRUCTOR, ROLE_STUDENT]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT)
    profile_picture = db.Column(db.String(255), nullable=True)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "profile_picture": self.profile_picture,
        }

    def __repr__(self):
        return f"<User {self.username}>"
