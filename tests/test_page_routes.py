from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.models.user import User


def create_extra_course(name="Algorithms", code="CSE301", description="Algo course"):
    course = Course(name=name, code=code, description=description)
    db.session.add(course)
    db.session.commit()
    return course


def create_extra_student(
    name="Another Student",
    student_id="12119999",
    username="anotherstudent",
    email="anotherstudent@example.com",
    password="Student1234",
):
    user = User(username=username, email=email, role="student")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(name=name, student_id=student_id, user_id=user.id)
    db.session.add(student)
    db.session.commit()
    return student


def create_student_without_profile(
    username="nostudentprofile",
    email="nostudentprofile@example.com",
    password="Student1234",
):
    user = User(username=username, email=email, role="student")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Flask Student Management Dashboard" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_student_dashboard_redirects_home_with_flash(auth_client):
    response = auth_client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Students do not have access to the management dashboard." in response.data
    assert b"Welcome to Flask Student Management Dashboard" in response.data


def test_instructor_dashboard_renders(instructor_client):
    response = instructor_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_unknown_html_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_html_method_not_allowed_returns_405_page(admin_client):
    response = admin_client.post("/dashboard")
    assert response.status_code == 405
    assert b"404 - Page Not Found" in response.data


def test_courses_page_requires_login(client):
    response = client.get("/courses", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_can_view_courses_page(admin_client):
    response = admin_client.get("/courses")
    assert response.status_code == 200
    assert b"All Courses" in response.data


def test_courses_page_search(admin_client):
    response = admin_client.get("/courses?search=Data")
    assert response.status_code == 200
    assert b"Data Structures" in response.data


def test_get_add_course_page(admin_client):
    response = admin_client.get("/courses/add")
    assert response.status_code == 200
    assert b"Add Course" in response.data


def test_student_cannot_access_add_course_page(auth_client):
    response = auth_client.get("/courses/add")
    assert response.status_code == 403
    assert b"403 - Access Denied" in response.data


def test_add_course_page_success(admin_client):
    response = admin_client.post(
        "/courses/add",
        data={
            "name": "Operating Systems",
            "code": "CSE303",
            "description": "OS course",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Course added successfully." in response.data
    assert b"Operating Systems" in response.data


def test_add_course_page_validation_error(admin_client):
    response = admin_client.post(
        "/courses/add",
        data={
            "name": "",
            "code": "",
            "description": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Add Course" in response.data
    assert b'name="name"' in response.data
    assert b'name="code"' in response.data


def test_edit_course_page_get(admin_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    response = admin_client.get(f"/courses/{course_id}/edit")
    assert response.status_code == 200
    assert b"Edit Course" in response.data


def test_edit_course_page_not_found(admin_client):
    response = admin_client.get("/courses/99999/edit")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_edit_course_page_success(admin_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    response = admin_client.post(
        f"/courses/{course_id}/edit",
        data={
            "name": "Data Structures Updated",
            "code": "CSE201",
            "description": "Updated description",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Course updated successfully." in response.data
    assert b"Data Structures Updated" in response.data


def test_delete_course_page_success(admin_client, app):
    with app.app_context():
        course = create_extra_course(name="Networks", code="CSE401")
        course_id = course.id

    response = admin_client.post(
        f"/courses/{course_id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Course deleted successfully." in response.data


def test_students_page_requires_login(client):
    response = client.get("/students", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_students_page_renders_for_admin(admin_client):
    response = admin_client.get("/students")
    assert response.status_code == 200
    assert b"Test Student" in response.data


def test_students_page_search(admin_client):
    response = admin_client.get("/students?search=12110001")
    assert response.status_code == 200
    assert b"Test Student" in response.data


def test_my_courses_page_for_student(auth_client):
    response = auth_client.get("/students/my-courses")
    assert response.status_code == 200
    assert b"My Courses" in response.data
    assert b"Test Student" in response.data


def test_my_courses_page_for_non_student_redirects(instructor_client):
    response = instructor_client.get("/students/my-courses", follow_redirects=True)
    assert response.status_code == 200
    assert b"This page is only available for student accounts." in response.data


def test_my_courses_page_for_student_without_profile_redirects(client, app):
    with app.app_context():
        create_student_without_profile()

    login(client, "nostudentprofile@example.com", "Student1234")
    response = client.get("/students/my-courses", follow_redirects=True)
    assert response.status_code == 200
    assert b"No student profile is linked to this account." in response.data


def test_get_add_student_page(admin_client):
    response = admin_client.get("/students/add")
    assert response.status_code == 200
    assert b"Add Student" in response.data


def test_add_student_page_success(admin_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    response = admin_client.post(
        "/students/add",
        data={
            "name": "New Page Student",
            "username": "newpagestudent",
            "email": "s12114444@stu.najah.edu",
            "password": "Student1234",
            "confirm_password": "Student1234",
            "course_ids": str(course_id),
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Student added successfully. Login email:" in response.data
    assert b"New Page Student" in response.data


def test_add_student_page_validation_error(admin_client):
    response = admin_client.post(
        "/students/add",
        data={
            "name": "Broken Student",
            "username": "brokenstudent",
            "email": "bad-email",
            "password": "Student1234",
            "confirm_password": "Student1234",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Add Student" in response.data
    assert b"Broken Student" in response.data
    assert b"brokenstudent" in response.data


def test_student_can_view_own_details(auth_client):
    response = auth_client.get("/students/12110001")
    assert response.status_code == 200
    assert b"Student Details" in response.data
    assert b"Test Student" in response.data


def test_student_cannot_view_other_student_details(client, app):
    with app.app_context():
        create_extra_student(
            name="Blocked Student",
            student_id="12118888",
            username="blockedstudent",
            email="blockedstudent@example.com",
        )

    login(client, "test@example.com", "Test1234")
    response = client.get("/students/12118888")
    assert response.status_code == 403
    assert b"403 - Access Denied" in response.data


def test_student_details_not_found(admin_client):
    response = admin_client.get("/students/00000000")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_edit_student_page_get(admin_client):
    response = admin_client.get("/students/12110001/edit")
    assert response.status_code == 200
    assert b"Edit Student" in response.data


def test_edit_student_page_validation_error_when_no_courses_selected(admin_client):
    response = admin_client.post(
        "/students/12110001/edit",
        data={"name": "Updated Student"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Select at least one course." in response.data


def test_edit_student_page_success(admin_client, app):
    with app.app_context():
        course = Course.query.filter_by(code="CSE201").first()
        course_id = course.id

    response = admin_client.post(
        "/students/12110001/edit",
        data={
            "name": "Updated Test Student",
            "course_ids": str(course_id),
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Student updated successfully." in response.data
    assert b"Updated Test Student" in response.data


def test_delete_student_page_success(admin_client, app):
    with app.app_context():
        create_extra_student(
            name="Delete Me",
            student_id="12117777",
            username="deleteme",
            email="deleteme@example.com",
        )

    response = admin_client.post(
        "/students/12117777/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Student deleted successfully." in response.data


def test_users_page_requires_admin(auth_client):
    response = auth_client.get("/users")
    assert response.status_code == 403
    assert b"403 - Access Denied" in response.data


def test_admin_can_view_users_page(admin_client):
    response = admin_client.get("/users")
    assert response.status_code == 200
    assert b"All Users" in response.data


def test_users_page_search(admin_client):
    response = admin_client.get("/users?search=admin")
    assert response.status_code == 200
    assert b"admin@example.com" in response.data


def test_get_add_user_page(admin_client):
    response = admin_client.get("/users/add")
    assert response.status_code == 200
    assert b"Add User" in response.data


def test_add_user_page_success(admin_client):
    response = admin_client.post(
        "/users/add",
        data={
            "username": "pageinstructor",
            "name": "Page Instructor",
            "email": "pageinstructor@najah.edu",
            "password": "Instructor123",
            "confirm_password": "Instructor123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"User added successfully." in response.data
    assert b"pageinstructor@najah.edu" in response.data


def test_add_user_page_validation_error(admin_client):
    response = admin_client.post(
        "/users/add",
        data={
            "username": "",
            "name": "",
            "email": "bad-email",
            "password": "123",
            "confirm_password": "456",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Add User" in response.data
    assert b"bad-email" in response.data


def test_user_details_page_success(admin_client, app):
    with app.app_context():
        admin_user = User.query.filter_by(email="admin@example.com").first()
        user_id = admin_user.id

    response = admin_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert b"admin@example.com" in response.data


def test_user_details_page_not_found(admin_client):
    response = admin_client.get("/users/99999")
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_edit_user_page_get(admin_client, app):
    with app.app_context():
        instructor = User.query.filter_by(email="instructor@example.com").first()
        user_id = instructor.id

    response = admin_client.get(f"/users/{user_id}/edit")
    assert response.status_code == 200
    assert b"Edit User" in response.data


def test_edit_user_page_success(admin_client, app):
    with app.app_context():
        instructor = User.query.filter_by(email="instructor@example.com").first()
        user_id = instructor.id

    response = admin_client.post(
        f"/users/{user_id}/edit",
        data={
            "username": "instructorupdated",
            "full_name": "Instructor Updated",
            "email": "instructorupdated@example.com",
            "password": "",
            "role": "instructor",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"User updated successfully." in response.data
    assert b"instructorupdated@example.com" in response.data


def test_delete_own_admin_page_blocked(admin_client, app):
    with app.app_context():
        admin_user = User.query.filter_by(email="admin@example.com").first()
        user_id = admin_user.id

    response = admin_client.post(f"/users/{user_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"You cannot delete your own admin account." in response.data


def test_delete_other_user_page_success(admin_client, app):
    with app.app_context():
        instructor = User.query.filter_by(email="instructor@example.com").first()
        user_id = instructor.id

    response = admin_client.post(f"/users/{user_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"User deleted successfully." in response.data
