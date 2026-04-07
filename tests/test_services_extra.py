import pytest

from app.extensions import db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.user import User
from app.services.dashboard_service import get_dashboard_stats
from app.services.service_exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.services.student_service import (
    ensure_student_access,
    get_courses_by_ids,
    get_student_courses_for_current_user,
    require_student,
)


def create_student_user_with_profile(
    username="svcstudent",
    email="svcstudent@example.com",
    student_id="12116666",
    name="Service Student",
):
    user = User(username=username, email=email, role="student")
    user.set_password("Student1234")
    db.session.add(user)
    db.session.flush()

    student = Student(name=name, student_id=student_id, user_id=user.id)
    db.session.add(student)
    db.session.commit()
    return user, student


def create_student_user_without_profile(
    username="svcstudentnoprofile",
    email="svcstudentnoprofile@example.com",
):
    user = User(username=username, email=email, role="student")
    user.set_password("Student1234")
    db.session.add(user)
    db.session.commit()
    return user


def create_instructor_user(
    username="svcinstructor",
    email="svcinstructor@example.com",
):
    user = User(username=username, email=email, role="instructor")
    user.set_password("Instructor1234")
    db.session.add(user)
    db.session.commit()
    return user


def test_get_dashboard_stats_for_instructor(app):
    with app.app_context():
        instructor = create_instructor_user()
        stats = get_dashboard_stats(instructor)

        assert "students_count" in stats
        assert "courses_count" in stats
        assert "users_count" in stats


def test_get_dashboard_stats_blocks_student(app):
    with app.app_context():
        student_user = User.query.filter_by(email="test@example.com").first()

        with pytest.raises(PermissionDeniedError) as exc:
            get_dashboard_stats(student_user)

        assert (
            str(exc.value) == "Students do not have access to the management dashboard."
        )


def test_get_student_courses_for_current_user_returns_student(app):
    with app.app_context():
        student_user = User.query.filter_by(email="test@example.com").first()
        student = get_student_courses_for_current_user(student_user)

        assert student.student_id == "12110001"


def test_get_student_courses_for_current_user_blocks_non_student(app):
    with app.app_context():
        instructor = create_instructor_user(username="inst2", email="inst2@example.com")

        with pytest.raises(PermissionDeniedError) as exc:
            get_student_courses_for_current_user(instructor)

        assert str(exc.value) == "This page is only available for student accounts."


def test_get_student_courses_for_current_user_requires_profile(app):
    with app.app_context():
        user = create_student_user_without_profile()

        with pytest.raises(ValidationError) as exc:
            get_student_courses_for_current_user(user)

        assert str(exc.value) == "No student profile is linked to this account."


def test_ensure_student_access_allows_own_profile(app):
    with app.app_context():
        student_user = User.query.filter_by(email="test@example.com").first()
        student = Student.query.filter_by(student_id="12110001").first()

        ensure_student_access(student_user, student)


def test_ensure_student_access_blocks_other_student(app):
    with app.app_context():
        student_user = User.query.filter_by(email="test@example.com").first()
        _, other_student = create_student_user_with_profile(
            username="otherstudent",
            email="otherstudent@example.com",
            student_id="12117776",
            name="Other Student",
        )

        with pytest.raises(PermissionDeniedError) as exc:
            ensure_student_access(student_user, other_student)

        assert str(exc.value) == "Access denied."


def test_ensure_student_access_requires_profile(app):
    with app.app_context():
        user = create_student_user_without_profile(
            username="studentnoprofile2",
            email="studentnoprofile2@example.com",
        )
        target_student = Student.query.filter_by(student_id="12110001").first()

        with pytest.raises(ValidationError) as exc:
            ensure_student_access(user, target_student)

        assert str(exc.value) == "No student profile is linked to this account."


def test_require_student_success(app):
    with app.app_context():
        student = require_student("12110001")
        assert student.name == "Test Student"


def test_require_student_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError) as exc:
            require_student("00000000")

        assert str(exc.value) == "Student not found."


def test_get_courses_by_ids_filters_invalid_and_duplicates(app):
    with app.app_context():
        course1 = Course.query.filter_by(code="CSE201").first()
        course2 = Course(name="Algorithms", code="CSE301", description="Algo")
        db.session.add(course2)
        db.session.commit()

        courses = get_courses_by_ids(
            [
                str(course1.id),
                str(course2.id),
                str(course1.id),
                "not-an-int",
                "99999",
                None,
            ]
        )

        assert len(courses) == 2
        ids = {course.id for course in courses}
        assert course1.id in ids
        assert course2.id in ids


def test_student_and_course_model_to_dict_with_enrollment(app):
    with app.app_context():
        student = Student.query.filter_by(student_id="12110001").first()
        course = Course.query.filter_by(code="CSE201").first()

        existing = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id,
        ).first()
        if existing is None:
            db.session.add(Enrollment(student_id=student.id, course_id=course.id))
            db.session.commit()

        student_data = student.to_dict()
        course_data = course.to_dict(include_students=True)

        assert student_data["student_id"] == "12110001"
        assert "courses_count" in student_data
        assert course_data["code"] == "CSE201"
        assert "students" in course_data
