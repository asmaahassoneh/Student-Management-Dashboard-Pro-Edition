def test_html_unauthorized_redirects_to_login(client):
    response = client.get("/students", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_unauthorized_returns_json_401(client):
    response = client.get("/api/students")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_html_404_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_api_404_json(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Resource not found."


def test_html_405_page(admin_client):
    response = admin_client.post("/dashboard")
    assert response.status_code == 405
    assert b"404 - Page Not Found" in response.data


def test_api_405_json(admin_client):
    response = admin_client.post("/api/students/12110001")
    assert response.status_code == 405
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Method not allowed."


def test_html_403_page(auth_client):
    response = auth_client.get("/users")
    assert response.status_code == 403
    assert b"403 - Access Denied" in response.data


def test_api_403_json(auth_client):
    response = auth_client.get("/api/users")
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Admin access required."
