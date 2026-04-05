from app.models.student import Student
from app.models.user import User


def create_student_user_payload(
    username="newstudent",
    email="s12115555@stu.najah.edu",
    password="Student123",
    name="New Student",
):
    return {
        "username": username,
        "email": email,
        "password": password,
        "name": name,
    }


def create_instructor_user_payload(
    username="newinstructor",
    email="instructor1@najah.edu",
    password="Instructor123",
):
    return {
        "username": username,
        "email": email,
        "password": password,
    }


def test_users_api_requires_login(client):
    response = client.get("/api/users")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_users_api_requires_admin(auth_client):
    response = auth_client.get("/api/users")
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Admin access required."


def test_admin_can_list_users(admin_client):
    response = admin_client.get("/api/users")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data


def test_get_user_by_id(admin_client):
    users_response = admin_client.get("/api/users")
    user_id = users_response.get_json()["data"][0]["id"]

    response = admin_client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "username" in data["data"]
    assert "email" in data["data"]
    assert "role" in data["data"]


def test_get_user_not_found(admin_client):
    response = admin_client.get("/api/users/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "User not found."


def test_create_student_user_success(admin_client, app):
    response = admin_client.post(
        "/api/users",
        json=create_student_user_payload(),
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == "newstudent"
    assert data["data"]["role"] == "student"
    assert data["data"]["email"] == "s12115555@stu.najah.edu"

    with app.app_context():
        user = User.query.filter_by(email="s12115555@stu.najah.edu").first()
        assert user is not None

        student = Student.query.filter_by(student_id="12115555").first()
        assert student is not None
        assert student.name == "New Student"
        assert student.user_id == user.id


def test_create_instructor_user_success(admin_client):
    response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(),
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == "newinstructor"
    assert data["data"]["role"] == "instructor"
    assert data["data"]["email"] == "instructor1@najah.edu"


def test_create_user_invalid_email(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "Valid1234",
            "name": "Bad Email",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email is not valid."


def test_create_user_non_university_email_rejected(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "outsideuser",
            "email": "outside@example.com",
            "password": "Valid1234",
            "name": "Outside User",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Please use a valid An-Najah email address."


def test_create_user_duplicate_username(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "s12117777@stu.najah.edu",
            "password": "Another123",
            "name": "Duplicate Username",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Username already exists."


def test_create_user_duplicate_email(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "Another123",
            "name": "Duplicate Email",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email already exists."


def test_create_student_user_requires_name(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "studentnoname",
            "email": "s12118888@stu.najah.edu",
            "password": "Student123",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "name is required for student accounts."


def test_update_user_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="olduser",
            email="olduser@najah.edu",
            password="Olduser123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "username": "updateduser",
            "email": "updateduser@najah.edu",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == "updateduser"
    assert data["data"]["email"] == "updateduser@najah.edu"


def test_update_user_password_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="changepass",
            email="changepass@najah.edu",
            password="Oldpass123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "password": "Newpass123",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_update_user_duplicate_username(admin_client):
    admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="userone",
            email="userone@najah.edu",
            password="Userone123",
        ),
    )

    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="usertwo",
            email="usertwo@najah.edu",
            password="Usertwo123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "username": "userone",
        },
    )

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Username already exists."


def test_update_user_duplicate_email(admin_client):
    admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="firstuser",
            email="firstuser@najah.edu",
            password="Firstuser123",
        ),
    )

    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="seconduser",
            email="seconduser@najah.edu",
            password="Seconduser123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "email": "firstuser@najah.edu",
        },
    )

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email already exists."


def test_update_user_invalid_email(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="emailtest",
            email="emailtest@najah.edu",
            password="Emailtest123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "email": "not-an-email",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email is not valid."


def test_update_user_weak_password(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="passtest",
            email="passtest@najah.edu",
            password="Passtest123",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "password": "123",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert (
        data["error"]
        == "Password must be at least 8 characters long and include both letters and numbers."
    )


def test_delete_user_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json=create_instructor_user_payload(
            username="deleteuser",
            email="deleteuser@najah.edu",
            password="Delete1234",
        ),
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204


def test_delete_user_not_found(admin_client):
    response = admin_client.delete("/api/users/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "User not found."


def test_admin_cannot_delete_self(admin_client):
    users_response = admin_client.get("/api/users")
    users = users_response.get_json()["data"]

    admin_id = None
    for user in users:
        if user["email"] == "admin@example.com":
            admin_id = user["id"]
            break

    assert admin_id is not None

    response = admin_client.delete(f"/api/users/{admin_id}")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "You cannot delete your own admin account."


def test_invalid_json_body_on_user_post(admin_client):
    response = admin_client.post(
        "/api/users",
        data="not-json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."


def test_users_unknown_route_returns_404(client):
    response = client.get("/api/users/unknown-route")
    assert response.status_code in (404, 405)


def test_users_method_not_allowed(admin_client):
    response = admin_client.patch("/api/users")
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method not allowed."
