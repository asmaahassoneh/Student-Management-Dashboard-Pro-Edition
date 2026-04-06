import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.models.user import User


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

        admin_user = User(
            username="adminuser",
            email="admin@example.com",
            role="admin",
        )
        admin_user.set_password("Admin1234")

        instructor_user = User(
            username="instructoruser",
            email="instructor@example.com",
            role="instructor",
        )
        instructor_user.set_password("Instructor1234")

        student_user = User(
            username="testuser",
            email="test@example.com",
            role="student",
        )
        student_user.set_password("Test1234")

        student_profile = Student(
            name="Test Student",
            student_id="12110001",
            user=student_user,
        )

        course = Course(
            name="Data Structures",
            code="CSE201",
            description="Test course",
        )

        db.session.add_all(
            [admin_user, instructor_user, student_user, student_profile, course]
        )
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "Test1234",
        },
        follow_redirects=True,
    )
    return client


@pytest.fixture
def admin_client(client):
    client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "Admin1234",
        },
        follow_redirects=True,
    )
    return client


@pytest.fixture
def instructor_client(client):
    client.post(
        "/login",
        data={
            "email": "instructor@example.com",
            "password": "Instructor1234",
        },
        follow_redirects=True,
    )
    return client
