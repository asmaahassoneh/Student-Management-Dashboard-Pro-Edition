from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.models.user import User
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.utils.role_helpers import extract_student_id
from app.utils.validators import (
    normalize_email,
    normalize_student_id,
    normalize_text,
    validate_student_form,
    validate_student_payload,
    validate_user_form,
)


def get_student_by_student_id(student_id):
    normalized_id = normalize_student_id(student_id)
    return Student.query.filter_by(student_id=normalized_id).first()


def require_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        raise NotFoundError("Student not found.")
    return student


def paginate_students(search=None, page=1, per_page=5):
    query = Student.query.order_by(Student.name.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (Student.name.ilike(f"%{search}%"))
            | (Student.student_id.ilike(f"%{search}%"))
        )

    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_courses_by_ids(course_ids):
    valid_courses = []

    for course_id in course_ids:
        try:
            course = db.session.get(Course, int(course_id))
            if course:
                valid_courses.append(course)
        except (TypeError, ValueError):
            continue

    return valid_courses


def get_all_courses_for_forms():
    return Course.query.order_by(Course.name.asc()).all()


def get_student_courses_for_current_user(current_user):
    if not current_user.is_student:
        raise PermissionDeniedError("This page is only available for student accounts.")

    student = current_user.student_profile
    if student is None:
        raise ValidationError("No student profile is linked to this account.")

    return student


def ensure_student_access(current_user, student):
    if current_user.is_student:
        if current_user.student_profile is None:
            raise ValidationError("No student profile is linked to this account.")

        if current_user.student_profile.student_id != student.student_id:
            raise PermissionDeniedError("Access denied.")


def validate_student_api_create(data):
    error = validate_student_payload(data)
    if error:
        raise ValidationError(error)

    normalized_id = normalize_student_id(data["student_id"])
    existing_student = Student.query.filter_by(student_id=normalized_id).first()
    if existing_student:
        raise ConflictError("Student ID already exists.")

    selected_courses = get_courses_by_ids(data.get("course_ids", []))

    return {
        "name": normalize_text(data["name"]),
        "student_id": normalized_id,
        "selected_courses": selected_courses,
    }


def validate_student_api_update(student, data):
    error = validate_student_payload(data, partial=True)
    if error:
        raise ValidationError(error)

    clean_data = {}

    if "name" in data:
        clean_data["name"] = normalize_text(data["name"])

    if "student_id" in data:
        new_student_id = normalize_student_id(data["student_id"])
        existing_student = Student.query.filter_by(student_id=new_student_id).first()
        if existing_student and existing_student.id != student.id:
            raise ConflictError("Student ID already exists.")
        clean_data["student_id"] = new_student_id

    selected_courses = None
    if "course_ids" in data:
        selected_courses = get_courses_by_ids(data["course_ids"])

    return clean_data, selected_courses


def validate_student_page_create(form_data, password, confirm_password):
    error = validate_student_form(
        form_data["name"],
        "12345678",
        form_data["course_ids"],
    )
    if error and "Student ID" not in error:
        raise ValidationError(error)

    user_error = validate_user_form(
        form_data["username"],
        form_data["email"],
        password,
        confirm_password,
        role=User.ROLE_STUDENT,
    )
    if user_error:
        raise ValidationError(user_error)

    student_id = extract_student_id(form_data["email"])
    if not student_id:
        raise ValidationError(
            "Student email must be in this format: sXXXXXXXX@stu.najah.edu"
        )

    existing_student = Student.query.filter_by(student_id=student_id).first()
    if existing_student:
        raise ConflictError("Student ID already exists.")

    existing_username = User.query.filter_by(
        username=normalize_text(form_data["username"])
    ).first()
    if existing_username:
        raise ConflictError("Username already exists.")

    existing_email = User.query.filter_by(
        email=normalize_email(form_data["email"])
    ).first()
    if existing_email:
        raise ConflictError("Email already exists.")

    return {
        "name": normalize_text(form_data["name"]),
        "username": normalize_text(form_data["username"]),
        "email": normalize_email(form_data["email"]),
        "student_id": student_id,
        "selected_courses": get_courses_by_ids(form_data["course_ids"]),
    }


def create_student(data, selected_courses=None):
    try:
        student = Student(
            name=normalize_text(data["name"]),
            student_id=normalize_student_id(data["student_id"]),
        )

        if selected_courses is not None:
            student.courses = selected_courses

        db.session.add(student)
        db.session.commit()
        return student

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database integrity error.") from exc


def create_student_with_user(form_data, password, confirm_password):
    clean_data = validate_student_page_create(form_data, password, confirm_password)

    try:
        user = User(
            username=clean_data["username"],
            email=clean_data["email"],
            role=User.ROLE_STUDENT,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        student = Student(
            name=clean_data["name"],
            student_id=clean_data["student_id"],
            user_id=user.id,
        )
        student.courses = clean_data["selected_courses"]

        db.session.add(student)
        db.session.commit()
        return user, student

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Something went wrong while saving the student.") from exc


def update_student(student, data, selected_courses=None):
    try:
        if "name" in data:
            student.name = normalize_text(data["name"])

        if "student_id" in data:
            student.student_id = normalize_student_id(data["student_id"])

        if selected_courses is not None:
            student.courses = selected_courses

        db.session.commit()
        return student

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def enroll_student_in_course(student, course):
    if course in student.courses:
        raise ConflictError("Student already enrolled in this course.")

    try:
        student.courses.append(course)
        db.session.commit()
        return student

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def unenroll_student_from_course(student, course):
    if course not in student.courses:
        raise ConflictError("Student is not enrolled in this course.")

    try:
        student.courses.remove(course)
        db.session.commit()
        return student

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError("Database error occurred.") from exc


def delete_student(student):
    try:
        db.session.delete(student)
        db.session.commit()

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ValidationError(
            "Something went wrong while deleting the student."
        ) from exc
