from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.services.student_service import (
    create_student,
    delete_student,
    enroll_student_in_course,
    get_courses_by_ids,
    get_student_by_student_id,
    update_student,
    unenroll_student_from_course,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import normalize_student_id, validate_student_payload

student_api_bp = Blueprint("student_api_bp", __name__, url_prefix="/api/students")


@student_api_bp.route("", methods=["GET"])
@login_required
def list_students():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Student.query.order_by(Student.name.asc())

    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%"))
            | (Student.student_id.ilike(f"%{search}%"))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (
        jsonify(
            {
                "success": True,
                "count": len(pagination.items),
                "total": pagination.total,
                "page": pagination.page,
                "pages": pagination.pages,
                "data": [student.to_dict() for student in pagination.items],
            }
        ),
        200,
    )


@student_api_bp.route("/<student_id>", methods=["GET"])
@login_required
def get_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found."}), 404
    return jsonify({"success": True, "data": student.to_dict()}), 200


@student_api_bp.route("", methods=["POST"])
@login_required
@admin_or_instructor_required
def add_student():
    data = request.get_json(silent=True)

    error = validate_student_payload(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    existing_student_id = Student.query.filter_by(
        student_id=normalize_student_id(data["student_id"])
    ).first()
    if existing_student_id:
        return jsonify({"success": False, "error": "Student ID already exists."}), 409

    course_ids = data.get("course_ids", [])
    selected_courses = get_courses_by_ids(course_ids)

    try:
        student = create_student(data, selected_courses)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Student created successfully.",
                    "data": student.to_dict(),
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400


@student_api_bp.route("/<student_id>", methods=["PUT"])
@login_required
@admin_or_instructor_required
def edit_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found."}), 404

    data = request.get_json(silent=True)
    error = validate_student_payload(data, partial=True)
    if error:
        return jsonify({"success": False, "error": error}), 400

    if "student_id" in data:
        new_student_id = normalize_student_id(data["student_id"])
        existing_student = Student.query.filter_by(student_id=new_student_id).first()
        if existing_student and existing_student.id != student.id:
            return (
                jsonify({"success": False, "error": "Student ID already exists."}),
                409,
            )

    selected_courses = None
    if "course_ids" in data:
        selected_courses = get_courses_by_ids(data["course_ids"])

    try:
        updated_student = update_student(student, data, selected_courses)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Student updated successfully.",
                    "data": updated_student.to_dict(),
                }
            ),
            200,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400


@student_api_bp.route("/<student_id>", methods=["DELETE"])
@login_required
@admin_or_instructor_required
def remove_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found."}), 404

    delete_student(student)
    return "", 204


@student_api_bp.route("/<student_id>/enroll", methods=["POST"])
@login_required
@admin_or_instructor_required
def enroll_course(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found."}), 404

    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "error": "course_id is required."}), 400

    course = db.session.get(Course, int(course_id))
    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    if course in student.courses:
        return (
            jsonify(
                {"success": False, "error": "Student already enrolled in this course."}
            ),
            409,
        )

    enroll_student_in_course(student, course)
    return (
        jsonify(
            {
                "success": True,
                "message": "Student enrolled successfully.",
                "data": student.to_dict(),
            }
        ),
        200,
    )


@student_api_bp.route("/<student_id>/unenroll", methods=["POST"])
@login_required
@admin_or_instructor_required
def unenroll_course(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found."}), 404

    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "error": "course_id is required."}), 400

    course = db.session.get(Course, int(course_id))
    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    if course not in student.courses:
        return (
            jsonify(
                {"success": False, "error": "Student is not enrolled in this course."}
            ),
            409,
        )

    unenroll_student_from_course(student, course)
    return (
        jsonify(
            {
                "success": True,
                "message": "Student unenrolled successfully.",
                "data": student.to_dict(),
            }
        ),
        200,
    )
