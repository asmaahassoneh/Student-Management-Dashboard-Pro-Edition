from app.extensions import db
from app.models.course import Course
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


def test_get_students_with_pagination(instructor_client, app):
    with app.app_context():
        for i in range(7):
            db.session.add(
                Student(
                    name=f"Student {i}",
                    student_id=f"1212000{i}",
                )
            )
        db.session.commit()

    response = instructor_client.get("/api/students?page=1&per_page=3")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 1
    assert data["pages"] >= 3
    assert len(data["data"]) == 3


def test_get_students_with_course_filter(instructor_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        student = Student(name="Filtered Student", student_id="12117777")
        db.session.add(student)
        db.session.commit()

        response = instructor_client.post(
            f"/api/students/{student.student_id}/enroll",
            json={"course_id": course.id},
        )
        assert response.status_code == 200

    response = instructor_client.get(f"/api/students?course_id={course.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert any(item["student_id"] == "12117777" for item in data["data"])


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


def test_get_student_courses_success(instructor_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        student = Student(name="Courses Student", student_id="12116666")
        db.session.add(student)
        db.session.commit()

        student_id = student.student_id
        course_id = course.id

    enroll_response = instructor_client.post(
        f"/api/students/{student_id}/enroll",
        json={"course_id": course_id},
    )
    assert enroll_response.status_code == 200

    response = instructor_client.get(f"/api/students/{student_id}/courses")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["data"][0]["code"] == "CSE201"


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
    assert data["data"]["student_id"] == "12112458"


def test_create_student_with_courses(instructor_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    payload = {
        "name": "Student With Course",
        "student_id": "12119991",
        "course_ids": [course_id],
    }

    response = instructor_client.post("/api/students", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["courses_count"] == 1


def test_enroll_student_success(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    response = instructor_client.post(
        "/api/students/12112458/enroll",
        json={"course_id": course_id},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["courses_count"] == 1


def test_enroll_student_duplicate(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    first_response = instructor_client.post(
        "/api/students/12112458/enroll",
        json={"course_id": course_id},
    )
    assert first_response.status_code == 200

    second_response = instructor_client.post(
        "/api/students/12112458/enroll",
        json={"course_id": course_id},
    )
    assert second_response.status_code == 409
    data = second_response.get_json()
    assert data["error"] == "Student already enrolled in this course."


def test_unenroll_student_success(instructor_client, app):
    with app.app_context():
        student = create_sample_student()
        db.session.add(student)
        db.session.commit()
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    instructor_client.post(
        "/api/students/12112458/enroll",
        json={"course_id": course_id},
    )

    response = instructor_client.post(
        "/api/students/12112458/unenroll",
        json={"course_id": course_id},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["courses_count"] == 0


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
