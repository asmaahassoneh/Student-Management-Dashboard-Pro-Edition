from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.student import Student
from app.models.user import User
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.utils.role_helpers import detect_role_and_student_id
from app.utils.validators import (
    is_valid_email,
    normalize_email,
    normalize_text,
    validate_user_form,
    validate_user_payload,
)


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


def require_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user


def paginate_users(search=None, page=1, per_page=5):
    query = User.query.order_by(User.username.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.role.ilike(f"%{search}%"))
        )

    return query.paginate(page=page, per_page=per_page, error_out=False)


def validate_user_api_create(data):
    if data is None:
        raise ValidationError("Request body must be valid JSON.")

    username = normalize_text(data.get("username", ""))
    email = normalize_email(data.get("email", ""))
    password = data.get("password", "")
    name = normalize_text(data.get("name", ""))

    missing_fields = []
    if not username:
        missing_fields.append("username")
    if not email:
        missing_fields.append("email")
    if not password:
        missing_fields.append("password")

    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}.")

    if User.query.filter_by(username=username).first():
        raise ConflictError("Username already exists.")

    if User.query.filter_by(email=email).first():
        raise ConflictError("Email already exists.")

    if not is_valid_email(email):
        raise ValidationError("Email is not valid.")

    role, extracted_student_id, role_error = detect_role_and_student_id(email)
    if role_error:
        raise ValidationError(role_error)

    if role == User.ROLE_STUDENT and not name:
        raise ValidationError("name is required for student accounts.")

    if role == User.ROLE_STUDENT:
        existing_student = Student.query.filter_by(
            student_id=extracted_student_id
        ).first()
        if existing_student:
            raise ConflictError("Student ID already exists.")

    return {
        "username": username,
        "email": email,
        "password": password,
        "name": name,
        "role": role,
        "student_id": extracted_student_id,
    }


def validate_user_page_create(username, email, password, confirm_password, name):
    error = validate_user_form(
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password,
    )
    if error:
        raise ValidationError(error)

    normalized_username = normalize_text(username)
    normalized_email = normalize_email(email)
    normalized_name = normalize_text(name)

    if User.query.filter_by(username=normalized_username).first():
        raise ConflictError("Username already exists.")

    if User.query.filter_by(email=normalized_email).first():
        raise ConflictError("Email already exists.")

    role, extracted_student_id, role_error = detect_role_and_student_id(
        normalized_email
    )
    if role_error:
        raise ValidationError(role_error)

    if role == User.ROLE_STUDENT:
        if not normalized_name:
            raise ValidationError("Full name is required for student accounts.")

        existing_student = Student.query.filter_by(
            student_id=extracted_student_id
        ).first()
        if existing_student:
            raise ConflictError("Student ID already exists.")

    return {
        "username": normalized_username,
        "full_name": normalized_name or None,
        "email": normalized_email,
        "password": password,
        "role": role,
        "student_id": extracted_student_id,
        "name": normalized_name,
    }


def validate_user_api_update(user, data):
    if data is None:
        raise ValidationError("Request body must be valid JSON.")

    error = validate_user_payload(data, partial=True)
    if error:
        raise ValidationError(error)

    clean_data = dict(data)

    if "username" in clean_data:
        clean_data["username"] = normalize_text(clean_data["username"])
        existing_username = User.query.filter_by(
            username=clean_data["username"]
        ).first()
        if existing_username and existing_username.id != user.id:
            raise ConflictError("Username already exists.")

    if "email" in clean_data:
        clean_data["email"] = normalize_email(clean_data["email"])
        existing_email = User.query.filter_by(email=clean_data["email"]).first()
        if existing_email and existing_email.id != user.id:
            raise ConflictError("Email already exists.")
        if not is_valid_email(clean_data["email"]):
            raise ValidationError("Email is not valid.")

    if "full_name" in clean_data:
        clean_data["full_name"] = normalize_text(clean_data["full_name"])

    return clean_data


def validate_user_page_update(user, username, email, password, role, full_name=""):
    error = validate_user_form(
        username,
        email,
        password=password,
        partial=True,
        role=role,
    )
    if error:
        raise ValidationError(error)

    normalized_username = normalize_text(username)
    normalized_email = normalize_email(email)
    normalized_full_name = normalize_text(full_name)

    existing_username = User.query.filter_by(username=normalized_username).first()
    if existing_username and existing_username.id != user.id:
        raise ConflictError("Username already exists.")

    existing_email = User.query.filter_by(email=normalized_email).first()
    if existing_email and existing_email.id != user.id:
        raise ConflictError("Email already exists.")

    return {
        "username": normalized_username,
        "email": normalized_email,
        "role": role,
        "password": password,
        "full_name": normalized_full_name or None,
    }


def create_user(data):
    try:
        user = User(
            username=normalize_text(data["username"]),
            full_name=normalize_text(data.get("full_name") or data.get("name", ""))
            or None,
            email=normalize_email(data["email"]),
            role=data.get("role", User.ROLE_STUDENT),
            profile_picture=data.get("profile_picture"),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.flush()

        if (
            data.get("role") == User.ROLE_STUDENT
            and data.get("student_id")
            and data.get("name")
        ):
            student = Student(
                name=normalize_text(data["name"]),
                student_id=data["student_id"],
                user_id=user.id,
            )
            db.session.add(student)

        db.session.commit()
        return user

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def update_user(user, data):
    try:
        if "username" in data:
            user.username = normalize_text(data["username"])

        if "email" in data:
            user.email = normalize_email(data["email"])

        if "role" in data:
            user.role = data["role"]

        if "full_name" in data:
            user.full_name = (
                normalize_text(data["full_name"]) if data["full_name"] else None
            )

        if "profile_picture" in data:
            user.profile_picture = data["profile_picture"]

        if "password" in data and data["password"]:
            user.set_password(data["password"])

        if user.student_profile and user.full_name:
            user.student_profile.name = user.full_name

        db.session.commit()
        return user

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def delete_user(user):
    try:
        if user.student_profile is not None:
            db.session.delete(user.student_profile)

        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Something went wrong while deleting the user.") from exc
