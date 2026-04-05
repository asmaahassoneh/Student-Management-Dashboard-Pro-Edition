from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.utils.validators import normalize_student_id, normalize_text


def get_all_students(search=None):
    query = Student.query.order_by(Student.name.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (Student.name.ilike(f"%{search}%"))
            | (Student.student_id.ilike(f"%{search}%"))
        )

    return query.all()


def get_student_by_student_id(student_id):
    normalized_id = normalize_student_id(student_id)
    return Student.query.filter_by(student_id=normalized_id).first()


def create_student(data, selected_courses):
    student = Student(
        name=normalize_text(data["name"]),
        student_id=normalize_student_id(data["student_id"]),
    )
    student.courses = selected_courses
    db.session.add(student)
    db.session.commit()
    return student


def update_student(student, data, selected_courses=None):
    if "name" in data:
        student.name = normalize_text(data["name"])

    if "student_id" in data:
        student.student_id = normalize_student_id(data["student_id"])

    if selected_courses is not None:
        student.courses = selected_courses

    db.session.commit()
    return student


def enroll_student_in_course(student, course):
    if course not in student.courses:
        student.courses.append(course)
        db.session.commit()
    return student


def unenroll_student_from_course(student, course):
    if course in student.courses:
        student.courses.remove(course)
        db.session.commit()
    return student


def delete_student(student):
    db.session.delete(student)
    db.session.commit()


def get_courses_by_ids(course_ids):
    valid_courses = []
    for course_id in course_ids:
        try:
            course = db.session.get(Course, int(course_id))
            if course:
                valid_courses.append(course)
        except (TypeError, ValueError):
            continue
    return valid_courses
