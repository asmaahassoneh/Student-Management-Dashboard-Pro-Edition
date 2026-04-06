from app.extensions import db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student


def test_enrollment_row_created_on_enroll(instructor_client, app):
    with app.app_context():
        student = Student(name="Relation Student", student_id="12117770")
        course = Course(name="Compiler Design", code="CSE470", description="Compiler")
        db.session.add_all([student, course])
        db.session.commit()
        student_id = student.student_id
        course_id = course.id

    response = instructor_client.post(
        f"/api/students/{student_id}/enroll",
        json={"course_id": course_id},
    )
    assert response.status_code == 200

    with app.app_context():
        enrollment = Enrollment.query.filter_by(course_id=course_id).first()
        assert enrollment is not None


def test_delete_student_cascades_enrollments(instructor_client, app):
    with app.app_context():
        student = Student(name="Cascade Student", student_id="12117771")
        course = Course(name="Security", code="CSE480", description="Security")
        db.session.add_all([student, course])
        db.session.commit()
        db.session.add(Enrollment(student_id=student.id, course_id=course.id))
        db.session.commit()

        student_id = student.student_id

    delete_response = instructor_client.delete(f"/api/students/{student_id}")
    assert delete_response.status_code == 204

    with app.app_context():
        assert Enrollment.query.count() == 0


def test_delete_course_cascades_enrollments(instructor_client, app):
    with app.app_context():
        student = Student(name="Cascade Student 2", student_id="12117772")
        course = Course(name="Machine Vision", code="CSE481", description="Vision")
        db.session.add_all([student, course])
        db.session.commit()
        db.session.add(Enrollment(student_id=student.id, course_id=course.id))
        db.session.commit()
        course_id = course.id

    delete_response = instructor_client.delete(f"/api/courses/{course_id}")
    assert delete_response.status_code == 204

    with app.app_context():
        assert Enrollment.query.count() == 0


def test_student_courses_count_matches_enrollments(app):
    with app.app_context():
        student = Student(name="Count Student", student_id="12117773")
        course1 = Course(name="Cloud", code="CSE482", description="Cloud")
        course2 = Course(name="DevOps", code="CSE483", description="DevOps")
        db.session.add_all([student, course1, course2])
        db.session.commit()

        db.session.add_all(
            [
                Enrollment(student_id=student.id, course_id=course1.id),
                Enrollment(student_id=student.id, course_id=course2.id),
            ]
        )
        db.session.commit()

        refreshed_student = Student.query.filter_by(student_id="12117773").first()
        assert refreshed_student.courses_count == 2
