from flask_login import login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.student import Student
from app.models.user import User
from app.services.service_exceptions import ConflictError, ValidationError
from app.utils.file_helpers import save_profile_picture
from app.utils.role_helpers import detect_role_and_student_id
from app.utils.validators import (
    normalize_email,
    normalize_text,
    validate_login_form,
    validate_register_form,
)


def register_user(form, files, upload_folder, allowed_extensions):
    name = normalize_text(form.get("name", ""))
    username = normalize_text(form.get("username", ""))
    email = normalize_email(form.get("email", ""))
    password = form.get("password", "")
    confirm_password = form.get("confirm_password", "")

    error = validate_register_form(username, email, password, confirm_password)
    if error:
        raise ValidationError(error)

    if not name:
        raise ValidationError("Full name is required.")

    role, extracted_student_id, role_error = detect_role_and_student_id(email)
    if role_error:
        raise ValidationError(role_error)

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        raise ConflictError("Username or email already exists.")

    if role == User.ROLE_STUDENT:
        existing_student = Student.query.filter_by(
            student_id=extracted_student_id
        ).first()
        if existing_student:
            raise ConflictError("Student ID already exists.")

    profile_picture_file = files.get("profile_picture")
    profile_picture = save_profile_picture(
        profile_picture_file,
        upload_folder,
        allowed_extensions,
    )

    user = User(
        username=username,
        email=email,
        role=role,
        profile_picture=profile_picture,
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()

        if role == User.ROLE_STUDENT:
            student = Student(
                name=name,
                student_id=extracted_student_id,
                user_id=user.id,
            )
            db.session.add(student)

        db.session.commit()
        return user

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError(
            "Something went wrong while creating your account."
        ) from exc


def authenticate_user(form):
    email = normalize_email(form.get("email", ""))
    password = form.get("password", "")

    error = validate_login_form(email, password)
    if error:
        raise ValidationError(error)

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        raise ValidationError("Invalid email or password.")

    login_user(user)
    return user


def logout_current_user():
    logout_user()
