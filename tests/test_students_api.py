from app.extensions import db
from app.models.student import Student


def create_sample_student():
    return Student(name="Asmaa Hassoneh", student_id="12112458")


def create_second_student():
    return Student(name="Another Student", student_id="12112459")


def test_get_students_requires_login(client):
    response = client.get("/api/students")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_get_students_success(auth_client):
    response = auth_client.get("/api/students")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data


def test_get_student_by_id_success(auth_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = auth_client.get("/api/students/12112458")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["student_id"] == "12112458"


def test_get_student_not_found(auth_client):
    response = auth_client.get("/api/students/00000000")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Student not found."


def test_student_cannot_create_student(auth_client):
    payload = {
        "name": "Asmaa Hassoneh",
        "student_id": "12112458",
    }

    response = auth_client.post("/api/students", json=payload)
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False


def test_instructor_can_create_student(instructor_client):
    payload = {
        "name": "Asmaa Hassoneh",
        "student_id": "12112458",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Asmaa Hassoneh"
    assert data["data"]["student_id"] == "12112458"


def test_create_student_normalizes_student_id(instructor_client):
    payload = {
        "name": "Asmaa Hassoneh",
        "student_id": "ab123",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["student_id"] == "AB123"


def test_create_student_missing_fields(instructor_client):
    payload = {
        "name": "Asmaa Hassoneh",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_create_student_empty_name(instructor_client):
    payload = {
        "name": "   ",
        "student_id": "12112458",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Name is required."


def test_create_student_invalid_student_id_format(instructor_client):
    payload = {
        "name": "Asmaa Hassoneh",
        "student_id": "12-112458",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Student ID must contain only letters and numbers."


def test_create_student_duplicate_student_id(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    payload = {
        "name": "Another Student",
        "student_id": "12112458",
    }

    response = instructor_client.post("/api/students", json=payload)

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Student ID already exists."


def test_student_cannot_update_student(auth_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = auth_client.put("/api/students/12112458", json={"name": "Updated"})
    assert response.status_code == 403


def test_update_student_success(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    payload = {
        "name": "Asmaa Updated",
    }

    response = instructor_client.put("/api/students/12112458", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Asmaa Updated"


def test_update_student_student_id_success(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = instructor_client.put(
        "/api/students/12112458",
        json={"student_id": "zz999"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["student_id"] == "ZZ999"


def test_update_student_duplicate_student_id(instructor_client, app):
    with app.app_context():
        student1 = create_sample_student()
        student2 = create_second_student()
        db.session.add_all([student1, student2])
        db.session.commit()

    payload = {
        "student_id": "12112459",
    }

    response = instructor_client.put("/api/students/12112458", json=payload)

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Student ID already exists."


def test_update_student_invalid_student_id(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    payload = {
        "student_id": "12-112458",
    }

    response = instructor_client.put("/api/students/12112458", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Student ID must contain only letters and numbers."


def test_update_student_empty_json_is_allowed(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = instructor_client.put("/api/students/12112458", json={})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_update_student_not_found(instructor_client):
    payload = {"name": "Updated Name"}

    response = instructor_client.put("/api/students/00000000", json=payload)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Student not found."


def test_student_cannot_delete_student(auth_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = auth_client.delete("/api/students/12112458")
    assert response.status_code == 403


def test_delete_student_success(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = instructor_client.delete("/api/students/12112458")

    assert response.status_code == 204


def test_delete_student_not_found(instructor_client):
    response = instructor_client.delete("/api/students/00000000")

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Student not found."


def test_invalid_json_body_on_post(instructor_client):
    response = instructor_client.post(
        "/api/students",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."


def test_invalid_json_body_on_put(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()

    response = instructor_client.put(
        "/api/students/12112458",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."


def test_students_unknown_route_returns_404(client):
    response = client.get("/api/unknown")

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Resource not found."


def test_students_method_not_allowed(auth_client):
    response = auth_client.patch("/api/students")

    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method not allowed."
