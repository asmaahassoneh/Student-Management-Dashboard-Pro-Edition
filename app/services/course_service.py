from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.course import Course
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.utils.validators import (
    normalize_course_code,
    normalize_text,
    validate_course_form,
    validate_course_payload,
)


def get_course_by_id(course_id):
    return db.session.get(Course, course_id)


def require_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        raise NotFoundError("Course not found.")
    return course


def paginate_courses(search=None, page=1, per_page=5):
    query = Course.query.order_by(Course.name.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (Course.name.ilike(f"%{search}%")) | (Course.code.ilike(f"%{search}%"))
        )

    return query.paginate(page=page, per_page=per_page, error_out=False)


def list_all_courses():
    return Course.query.order_by(Course.name.asc()).all()


def validate_course_create_data(data, is_api=False):
    if is_api:
        error = validate_course_payload(data)
    else:
        error = validate_course_form(data.get("name", ""), data.get("code", ""))

    if error:
        raise ValidationError(error)

    normalized_name = normalize_text(data["name"])
    normalized_code = normalize_course_code(data["code"])

    existing_name = Course.query.filter_by(name=normalized_name).first()
    if existing_name:
        raise ConflictError("Course name already exists.")

    existing_code = Course.query.filter_by(code=normalized_code).first()
    if existing_code:
        raise ConflictError("Course code already exists.")

    return {
        "name": normalized_name,
        "code": normalized_code,
        "description": normalize_text(data.get("description", "")) or None,
    }


def validate_course_update_data(course, data, is_api=False):
    if is_api:
        error = validate_course_payload(data, partial=True)
    else:
        error = validate_course_form(data.get("name", ""), data.get("code", ""))

    if error:
        raise ValidationError(error)

    normalized_name = normalize_text(data["name"]) if "name" in data else course.name
    normalized_code = (
        normalize_course_code(data["code"]) if "code" in data else course.code
    )
    normalized_description = (
        normalize_text(data.get("description", "")) or None
        if "description" in data
        else course.description
    )

    existing_name = Course.query.filter_by(name=normalized_name).first()
    if existing_name and existing_name.id != course.id:
        raise ConflictError("Course name already exists.")

    existing_code = Course.query.filter_by(code=normalized_code).first()
    if existing_code and existing_code.id != course.id:
        raise ConflictError("Course code already exists.")

    return {
        "name": normalized_name,
        "code": normalized_code,
        "description": normalized_description,
    }


def create_course(data):
    clean_data = validate_course_create_data(data, is_api=isinstance(data, dict))

    course = Course(
        name=clean_data["name"],
        code=clean_data["code"],
        description=clean_data["description"],
    )

    try:
        db.session.add(course)
        db.session.commit()
        return course
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def update_course(course, data):
    clean_data = validate_course_update_data(
        course, data, is_api=isinstance(data, dict)
    )

    try:
        course.name = clean_data["name"]
        course.code = clean_data["code"]
        course.description = clean_data["description"]
        db.session.commit()
        return course
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def delete_course(course):
    try:
        db.session.delete(course)
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError(
            "Something went wrong while deleting the course."
        ) from exc
