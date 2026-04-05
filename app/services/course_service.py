from app.extensions import db
from app.models.course import Course
from app.utils.validators import normalize_course_code, normalize_text


def get_all_courses(search=None):
    query = Course.query.order_by(Course.name.asc())

    if search:
        search = normalize_text(search)
        query = query.filter(
            (Course.name.ilike(f"%{search}%")) | (Course.code.ilike(f"%{search}%"))
        )

    return query.all()


def get_course_by_id(course_id):
    return db.session.get(Course, course_id)


def create_course(data):
    course = Course(
        name=normalize_text(data["name"]),
        code=normalize_course_code(data["code"]),
        description=normalize_text(data.get("description", "")) or None,
    )
    db.session.add(course)
    db.session.commit()
    return course


def update_course(course, data):
    if "name" in data:
        course.name = normalize_text(data["name"])

    if "code" in data:
        course.code = normalize_course_code(data["code"])

    if "description" in data:
        course.description = normalize_text(data["description"]) or None

    db.session.commit()
    return course


def delete_course(course):
    db.session.delete(course)
    db.session.commit()
