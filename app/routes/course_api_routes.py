from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.services.course_service import (
    create_course,
    paginate_courses,
    require_course,
    update_course,
    delete_course,
)
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.utils.decorators import admin_or_instructor_required

course_api_bp = Blueprint("course_api_bp", __name__, url_prefix="/api/courses")


@course_api_bp.route("", methods=["GET"])
@login_required
def list_courses():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    student_db_id = request.args.get("student_db_id", type=int)

    pagination = paginate_courses(
        search=search,
        student_id=student_db_id,
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
                    "student_db_id": student_db_id,
                },
                "data": [course.to_dict() for course in pagination.items],
            }
        ),
        200,
    )


@course_api_bp.route("/<int:course_id>", methods=["GET"])
@login_required
def get_course(course_id):
    try:
        course = require_course(course_id)
        return (
            jsonify({"success": True, "data": course.to_dict(include_students=True)}),
            200,
        )
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404


@course_api_bp.route("/<int:course_id>/students", methods=["GET"])
@login_required
def get_course_students(course_id):
    try:
        course = require_course(course_id)
        return (
            jsonify(
                {
                    "success": True,
                    "course_id": course.id,
                    "count": len(course.students),
                    "data": [student.to_dict() for student in course.students],
                }
            ),
            200,
        )
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404


@course_api_bp.route("", methods=["POST"])
@login_required
@admin_or_instructor_required
def add_course():
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
        course = create_course(data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Course created successfully.",
                    "data": course.to_dict(),
                }
            ),
            201,
        )
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@course_api_bp.route("/<int:course_id>", methods=["PUT"])
@login_required
@admin_or_instructor_required
def edit_course(course_id):
    try:
        course = require_course(course_id)
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
        updated_course = update_course(course, data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Course updated successfully.",
                    "data": updated_course.to_dict(),
                }
            ),
            200,
        )
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@course_api_bp.route("/<int:course_id>", methods=["DELETE"])
@login_required
@admin_or_instructor_required
def remove_course(course_id):
    try:
        course = require_course(course_id)
        delete_course(course)
        return "", 204
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
