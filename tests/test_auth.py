from app.extensions import db
from app.models.student import Student
from app.models.user import User


def create_user(
    app,
    username="asmaa",
    email="s12119999@stu.najah.edu",
    password="asmaa1234",
    role="student",
):
    with app.app_context():
        existing_user = User.query.filter_by(email=email).first()
        if existing_user is None:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            if role == "student":
                local_part = email.split("@")[0]
                if local_part.startswith("s") and local_part[1:].isdigit():
                    student_id = local_part[1:]
                    existing_student = Student.query.filter_by(
                        student_id=student_id
                    ).first()
                    if existing_student is None:
                        student = Student(
                            name="Existing Student",
                            student_id=student_id,
                            user_id=user.id,
                        )
                        db.session.add(student)

            db.session.commit()


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_register_student_success(client, app):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "s12112458@stu.najah.edu",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="s12112458@stu.najah.edu").first()
        assert user is not None
        assert user.username == "asmaa"
        assert user.role == "student"

        student = Student.query.filter_by(student_id="12112458").first()
        assert student is not None
        assert student.name == "Asmaa Hassoneh"
        assert student.user_id == user.id


def test_register_duplicate_user(client, app):
    create_user(
        app,
        username="asmaa",
        email="s12112458@stu.najah.edu",
        password="asmaa1234",
        role="student",
    )

    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "s12112458@stu.najah.edu",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Username or email already exists." in response.data


def test_register_invalid_email_format(client):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "invalid-email",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Email is not valid." in response.data


def test_register_rejects_non_university_email(client):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "asmaa@example.com",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please use a valid An-Najah email address." in response.data


def test_register_rejects_bad_student_email_pattern(client):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "asmaa@stu.najah.edu",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid student email format." in response.data


def test_register_passwords_do_not_match(client):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "s12112458@stu.najah.edu",
            "password": "asmaa1234",
            "confirm_password": "wrong1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_register_weak_password(client):
    response = client.post(
        "/register",
        data={
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "s12112458@stu.najah.edu",
            "password": "123",
            "confirm_password": "123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Password must be at least 8 characters long and include both letters and numbers."
        in response.data
    )


def test_login_success_student(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200


def test_login_success_admin(admin_client):
    response = admin_client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200


def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        data={
            "email": "wrong@example.com",
            "password": "wrongpass123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_logout(auth_client):
    response = auth_client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully." in response.data
