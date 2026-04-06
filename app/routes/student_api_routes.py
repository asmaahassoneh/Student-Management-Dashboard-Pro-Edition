from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.extensions import db
from app.models.course import Course
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.services.student_service import (
    create_student,
    delete_student,
    enroll_student_in_course,
    paginate_students,
    require_student,
    unenroll_student_from_course,
    update_student,
    validate_student_api_create,
    validate_student_api_update,
)
from app.utils.decorators import admin_or_instructor_required

student_api_bp = Blueprint("student_api_bp", __name__, url_prefix="/api/students")


@student_api_bp.route("", methods=["GET"])
@login_required
def list_students():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    course_id = request.args.get("course_id", type=int)

    pagination = paginate_students(
        search=search,
        course_id=course_id,
        page=page,
        per_page=per_page,
    )

    return (
        jsonify(
            {
                "success": True,
                "count": len(pagination.items),
                "total": pagination.total,
                "page": pagination.page,
                "pages": pagination.pages,
                "filters": {
                    "search": search,
                    "course_id": course_id,
                },
                "data": [student.to_dict() for student in pagination.items],
            }
        ),
        200,
    )


@student_api_bp.route("/<student_id>", methods=["GET"])
@login_required
def get_student(student_id):
    try:
        student = require_student(student_id)
        return jsonify({"success": True, "data": student.to_dict()}), 200
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404


@student_api_bp.route("/<student_id>/courses", methods=["GET"])
@login_required
def get_student_courses(student_id):
    try:
        student = require_student(student_id)
        return (
            jsonify(
                {
                    "success": True,
                    "student_id": student.student_id,
                    "count": len(student.courses),
                    "data": [course.to_dict() for course in student.courses],
                }
            ),
            200,
        )
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404


@student_api_bp.route("", methods=["POST"])
@login_required
@admin_or_instructor_required
def add_student():
    data = request.get_json(silent=True)
    if data is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    try:
        clean_data = validate_student_api_create(data)
        student = create_student(
            {
                "name": clean_data["name"],
                "student_id": clean_data["student_id"],
            },
            clean_data["selected_courses"],
        )
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
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@student_api_bp.route("/<student_id>", methods=["PUT"])
@login_required
@admin_or_instructor_required
def edit_student(student_id):
    try:
        student = require_student(student_id)
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404

    data = request.get_json(silent=True)
    if data is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    try:
        clean_data, selected_courses = validate_student_api_update(student, data)
        updated_student = update_student(student, clean_data, selected_courses)
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
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@student_api_bp.route("/<student_id>", methods=["DELETE"])
@login_required
@admin_or_instructor_required
def remove_student(student_id):
    try:
        student = require_student(student_id)
        delete_student(student)
        return "", 204
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@student_api_bp.route("/<student_id>/enroll", methods=["POST"])
@login_required
@admin_or_instructor_required
def enroll_course(student_id):
    try:
        student = require_student(student_id)
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404

    data = request.get_json(silent=True)
    if data is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "error": "course_id is required."}), 400

    try:
        course = db.session.get(Course, int(course_id))
    except (TypeError, ValueError):
        course = None

    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    try:
        updated_student = enroll_student_in_course(student, course)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Student enrolled successfully.",
                    "data": updated_student.to_dict(),
                }
            ),
            200,
        )
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@student_api_bp.route("/<student_id>/unenroll", methods=["POST"])
@login_required
@admin_or_instructor_required
def unenroll_course(student_id):
    try:
        student = require_student(student_id)
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404

    data = request.get_json(silent=True)
    if data is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "error": "course_id is required."}), 400

    try:
        course = db.session.get(Course, int(course_id))
    except (TypeError, ValueError):
        course = None

    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    try:
        updated_student = unenroll_student_from_course(student, course)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Student unenrolled successfully.",
                    "data": updated_student.to_dict(),
                }
            ),
            200,
        )
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409
