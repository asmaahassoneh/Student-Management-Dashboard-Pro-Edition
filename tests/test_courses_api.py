from app.extensions import db
from app.models.course import Course
from app.models.student import Student


def test_get_courses_with_pagination(auth_client, app):
    with app.app_context():
        for i in range(6):
            db.session.add(
                Course(
                    name=f"Course {i}",
                    code=f"CSE5{i}0",
                    description="Extra course",
                )
            )
        db.session.commit()

    response = auth_client.get("/api/courses?page=1&per_page=3")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 1
    assert len(data["data"]) == 3


def test_get_course_students_success(instructor_client, app):
    with app.app_context():
        course = Course(name="Networks", code="CSE401", description="Networks")
        student = Student(name="API Student", student_id="12118888")
        db.session.add_all([course, student])
        db.session.commit()

        course_id = course.id
        student_id = student.student_id

    enroll_response = instructor_client.post(
        f"/api/students/{student_id}/enroll",
        json={"course_id": course_id},
    )
    assert enroll_response.status_code == 200

    response = instructor_client.get(f"/api/courses/{course_id}/students")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["data"][0]["student_id"] == "12118888"


def test_filter_courses_by_student_db_id(instructor_client, app):
    with app.app_context():
        course = Course(name="AI", code="CSE450", description="AI")
        student = Student(name="Filter Student", student_id="12119998")
        db.session.add_all([course, student])
        db.session.commit()
        course_id = course.id
        student_student_id = student.student_id
        student_db_id = student.id

    enroll_response = instructor_client.post(
        f"/api/students/{student_student_id}/enroll",
        json={"course_id": course_id},
    )
    assert enroll_response.status_code == 200

    response = instructor_client.get(f"/api/courses?student_db_id={student_db_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert any(item["code"] == "CSE450" for item in data["data"])


def test_get_courses_requires_login(client):
    response = client.get("/api/courses")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Authentication required."


def test_get_courses(auth_client):
    response = auth_client.get("/api/courses")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data


def test_get_course_by_id(auth_client, app):
    with app.app_context():
        course = Course(
            name="Algorithms", code="CSE301", description="Algorithms course"
        )
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    response = auth_client.get(f"/api/courses/{course_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Algorithms"


def test_get_course_not_found(auth_client):
    response = auth_client.get("/api/courses/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Course not found."


def test_student_cannot_create_course(auth_client):
    response = auth_client.post(
        "/api/courses",
        json={
            "name": "Microprocessors",
            "code": "CPE330",
            "description": "Processor systems",
        },
    )
    assert response.status_code == 403


def test_create_course(instructor_client):
    response = instructor_client.post(
        "/api/courses",
        json={
            "name": "Microprocessors",
            "code": "CPE330",
            "description": "Processor systems",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Microprocessors"


def test_create_course_missing_fields(instructor_client):
    response = instructor_client.post(
        "/api/courses",
        json={
            "name": "Microprocessors",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_create_course_invalid_code(instructor_client):
    response = instructor_client.post(
        "/api/courses",
        json={
            "name": "Microprocessors",
            "code": "CPE@330",
            "description": "Processor systems",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Course code must contain only letters, numbers, or dashes."


def test_create_course_duplicate_name(instructor_client, app):
    with app.app_context():
        course = Course(name="Operating Systems", code="CSE410", description="OS")
        db.session.add(course)
        db.session.commit()

    response = instructor_client.post(
        "/api/courses",
        json={
            "name": "Operating Systems",
            "code": "CSE411",
            "description": "Another one",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Course name already exists."


def test_create_course_duplicate_code(instructor_client, app):
    with app.app_context():
        course = Course(name="Networks", code="CSE420", description="Networks")
        db.session.add(course)
        db.session.commit()

    response = instructor_client.post(
        "/api/courses",
        json={
            "name": "Computer Networks 2",
            "code": "CSE420",
            "description": "Duplicate code",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Course code already exists."


def test_update_course(instructor_client, app):
    with app.app_context():
        course = Course(name="Databases", code="CSE350", description="DB")
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    response = instructor_client.put(
        f"/api/courses/{course_id}",
        json={"description": "Updated DB course"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["description"] == "Updated DB course"


def test_update_course_name_and_code(instructor_client, app):
    with app.app_context():
        course = Course(name="AI", code="CSE460", description="AI")
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    response = instructor_client.put(
        f"/api/courses/{course_id}",
        json={"name": "Artificial Intelligence", "code": "CSE461"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "Artificial Intelligence"
    assert data["data"]["code"] == "CSE461"


def test_update_course_not_found(instructor_client):
    response = instructor_client.put(
        "/api/courses/99999",
        json={"description": "Updated"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Course not found."


def test_update_course_duplicate_name(instructor_client, app):
    with app.app_context():
        c1 = Course(name="Course One", code="ONE101", description="desc")
        c2 = Course(name="Course Two", code="TWO101", description="desc")
        db.session.add_all([c1, c2])
        db.session.commit()
        course_id = c2.id

    response = instructor_client.put(
        f"/api/courses/{course_id}",
        json={"name": "Course One"},
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Course name already exists."


def test_update_course_duplicate_code(instructor_client, app):
    with app.app_context():
        c1 = Course(name="Course A", code="AAA101", description="desc")
        c2 = Course(name="Course B", code="BBB101", description="desc")
        db.session.add_all([c1, c2])
        db.session.commit()
        course_id = c2.id

    response = instructor_client.put(
        f"/api/courses/{course_id}",
        json={"code": "AAA101"},
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Course code already exists."


def test_delete_course(instructor_client, app):
    with app.app_context():
        course = Course(
            name="Microprocessors", code="CPE330", description="Processor systems"
        )
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    response = instructor_client.delete(f"/api/courses/{course_id}")
    assert response.status_code == 204


def test_delete_course_not_found(instructor_client):
    response = instructor_client.delete("/api/courses/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Course not found."


def test_invalid_json_body_on_course_post(instructor_client):
    response = instructor_client.post(
        "/api/courses",
        data="not-json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."


def test_invalid_json_body_on_course_put(instructor_client, app):
    with app.app_context():
        course = Course(name="Compiler", code="CSE470", description="Compiler")
        db.session.add(course)
        db.session.commit()
        course_id = course.id

    response = instructor_client.put(
        f"/api/courses/{course_id}",
        data="not-json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Request body must be valid JSON."
