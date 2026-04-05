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


def test_create_user_success(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Newuser123",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == "newuser"
    assert data["data"]["role"] == "student"


def test_create_admin_user_success(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "admin2",
            "email": "admin2@example.com",
            "password": "Admin2345",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["role"] == "admin"


def test_create_user_invalid_email(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "Valid1234",
            "role": "student",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email is not valid."


def test_create_user_weak_password(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "weakpass",
            "email": "weakpass@example.com",
            "password": "123",
            "role": "student",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert (
        data["error"]
        == "Password must be at least 8 characters long and include both letters and numbers."
    )


def test_create_user_duplicate_username(admin_client):
    response = admin_client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "Another123",
            "role": "student",
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
            "role": "student",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email already exists."


def test_update_user_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "olduser",
            "email": "olduser@example.com",
            "password": "Olduser123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "role": "instructor",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["username"] == "updateduser"
    assert data["data"]["email"] == "updateduser@example.com"
    assert data["data"]["role"] == "instructor"


def test_update_user_password_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "changepass",
            "email": "changepass@example.com",
            "password": "Oldpass123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={"password": "Newpass123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_update_user_duplicate_username(admin_client):
    admin_client.post(
        "/api/users",
        json={
            "username": "userone",
            "email": "userone@example.com",
            "password": "Userone123",
            "role": "student",
        },
    )
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "usertwo",
            "email": "usertwo@example.com",
            "password": "Usertwo123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={"username": "userone"},
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Username already exists."


def test_update_user_duplicate_email(admin_client):
    admin_client.post(
        "/api/users",
        json={
            "username": "firstuser",
            "email": "firstuser@example.com",
            "password": "Firstuser123",
            "role": "student",
        },
    )
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "seconduser",
            "email": "seconduser@example.com",
            "password": "Seconduser123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={"email": "firstuser@example.com"},
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email already exists."


def test_update_user_invalid_email(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "emailtest",
            "email": "emailtest@example.com",
            "password": "Emailtest123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={"email": "invalid-email"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email is not valid."


def test_update_user_weak_password(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "passtest",
            "email": "passtest@example.com",
            "password": "Passtest123",
            "role": "student",
        },
    )
    user_id = create_response.get_json()["data"]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        json={"password": "123"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert (
        data["error"]
        == "Password must be at least 8 characters long and include both letters and numbers."
    )


def test_update_user_not_found(admin_client):
    response = admin_client.put(
        "/api/users/99999",
        json={"username": "updated"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "User not found."


def test_delete_user_success(admin_client):
    create_response = admin_client.post(
        "/api/users",
        json={
            "username": "deleteuser",
            "email": "deleteuser@example.com",
            "password": "Delete1234",
            "role": "student",
        },
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

    admin_user = next(user for user in users if user["email"] == "admin@example.com")

    response = admin_client.delete(f"/api/users/{admin_user['id']}")
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


def test_invalid_json_body_on_user_put(admin_client):
    users_response = admin_client.get("/api/users")
    user_id = users_response.get_json()["data"][0]["id"]

    response = admin_client.put(
        f"/api/users/{user_id}",
        data="not-json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."
