from app.extensions import db
from app.models.user import User


def create_user(
    app,
    username="asmaa",
    email="asmaa@example.com",
    password="asmaa1234",
    role="student",
):
    with app.app_context():
        existing_user = User.query.filter_by(email=email).first()
        if existing_user is None:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_register_success(client, app):
    response = client.post(
        "/register",
        data={
            "username": "asmaa",
            "email": "asmaa@example.com",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="asmaa@example.com").first()
        assert user is not None
        assert user.username == "asmaa"


def test_register_duplicate_user(client, app):
    create_user(app, username="asmaa", email="asmaa@example.com")

    response = client.post(
        "/register",
        data={
            "username": "asmaa",
            "email": "asmaa@example.com",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Username or email already exists." in response.data


def test_register_invalid_email(client):
    response = client.post(
        "/register",
        data={
            "username": "asmaa",
            "email": "invalid-email",
            "password": "asmaa1234",
            "confirm_password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Email is not valid." in response.data


def test_register_password_mismatch(client):
    response = client.post(
        "/register",
        data={
            "username": "asmaa",
            "email": "asmaa@example.com",
            "password": "asmaa1234",
            "confirm_password": "different1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_register_weak_password(client):
    response = client.post(
        "/register",
        data={
            "username": "asmaa",
            "email": "asmaa@example.com",
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


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client, app):
    create_user(app, username="asmaa", email="asmaa@example.com", password="asmaa1234")

    response = client.post(
        "/login",
        data={
            "email": "asmaa@example.com",
            "password": "asmaa1234",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Login successful." in response.data


def test_login_invalid_credentials(client, app):
    create_user(app, username="asmaa", email="asmaa@example.com", password="asmaa1234")

    response = client.post(
        "/login",
        data={
            "email": "asmaa@example.com",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in [302, 401]


def test_dashboard_access_after_login(client, app):
    create_user(app, username="asmaa", email="asmaa@example.com", password="asmaa1234")

    client.post(
        "/login",
        data={
            "email": "asmaa@example.com",
            "password": "asmaa1234",
        },
        follow_redirects=True,
    )

    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_logout(client, app):
    create_user(app, username="asmaa", email="asmaa@example.com", password="asmaa1234")

    client.post(
        "/login",
        data={
            "email": "asmaa@example.com",
            "password": "asmaa1234",
        },
        follow_redirects=True,
    )

    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully." in response.data


def test_logout_requires_login(client):
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data


def test_404_page_html(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404


def test_403_page_html(auth_client):
    response = auth_client.get("/users", follow_redirects=False)
    assert response.status_code == 403
