from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.course import Course
from app.services.course_service import (
    create_course,
    get_course_by_id,
    update_course,
    delete_course,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import normalize_course_code, validate_course_payload

course_api_bp = Blueprint("course_api_bp", __name__, url_prefix="/api/courses")


@course_api_bp.route("", methods=["GET"])
@login_required
def list_courses():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Course.query.order_by(Course.name.asc())

    if search:
        query = query.filter(
            (Course.name.ilike(f"%{search}%")) | (Course.code.ilike(f"%{search}%"))
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
                "data": [course.to_dict() for course in pagination.items],
            }
        ),
        200,
    )


@course_api_bp.route("/<int:course_id>", methods=["GET"])
@login_required
def get_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404
    return jsonify({"success": True, "data": course.to_dict()}), 200


@course_api_bp.route("", methods=["POST"])
@login_required
@admin_or_instructor_required
def add_course():
    data = request.get_json(silent=True)

    error = validate_course_payload(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    existing_name = Course.query.filter_by(name=data["name"].strip()).first()
    if existing_name:
        return jsonify({"success": False, "error": "Course name already exists."}), 409

    existing_code = Course.query.filter_by(
        code=normalize_course_code(data["code"])
    ).first()
    if existing_code:
        return jsonify({"success": False, "error": "Course code already exists."}), 409

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
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400


@course_api_bp.route("/<int:course_id>", methods=["PUT"])
@login_required
@admin_or_instructor_required
def edit_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    data = request.get_json(silent=True)
    error = validate_course_payload(data, partial=True)
    if error:
        return jsonify({"success": False, "error": error}), 400

    if "name" in data:
        existing_name = Course.query.filter_by(name=data["name"].strip()).first()
        if existing_name and existing_name.id != course.id:
            return (
                jsonify({"success": False, "error": "Course name already exists."}),
                409,
            )

    if "code" in data:
        new_code = normalize_course_code(data["code"])
        existing_code = Course.query.filter_by(code=new_code).first()
        if existing_code and existing_code.id != course.id:
            return (
                jsonify({"success": False, "error": "Course code already exists."}),
                409,
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
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400


@course_api_bp.route("/<int:course_id>", methods=["DELETE"])
@login_required
@admin_or_instructor_required
def remove_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        return jsonify({"success": False, "error": "Course not found."}), 404

    delete_course(course)
    return "", 204
