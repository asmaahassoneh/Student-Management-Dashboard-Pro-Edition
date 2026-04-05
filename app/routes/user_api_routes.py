from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.student import Student
from app.models.user import User
from app.services.user_service import delete_user, get_user_by_id, update_user
from app.utils.decorators import admin_required
from app.utils.validators import (
    normalize_email,
    normalize_text,
    validate_user_payload,
    is_valid_email,
)
from app.utils.role_helpers import detect_role_and_student_id

user_api_bp = Blueprint("user_api_bp", __name__, url_prefix="/api/users")


@user_api_bp.route("", methods=["POST"])
@login_required
@admin_required
def create_user():
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

    username = normalize_text(data.get("username", ""))
    email = normalize_email(data.get("email", ""))
    password = data.get("password", "")
    name = normalize_text(data.get("name", ""))

    missing_fields = []
    if not username:
        missing_fields.append("username")
    if not email:
        missing_fields.append("email")
    if not password:
        missing_fields.append("password")

    if missing_fields:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}.",
                }
            ),
            400,
        )

    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return jsonify({"success": False, "error": "Username already exists."}), 409

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"success": False, "error": "Email already exists."}), 409

    if not is_valid_email(email):
        return jsonify({"success": False, "error": "Email is not valid."}), 400

    role, extracted_student_id, role_error = detect_role_and_student_id(email)
    if role_error:
        return jsonify({"success": False, "error": role_error}), 400

    if role == User.ROLE_STUDENT and not name:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "name is required for student accounts.",
                }
            ),
            400,
        )

    if role == User.ROLE_STUDENT:
        existing_student = Student.query.filter_by(
            student_id=extracted_student_id
        ).first()
        if existing_student:
            return (
                jsonify({"success": False, "error": "Student ID already exists."}),
                409,
            )

    try:
        user = User(
            username=username,
            email=email,
            role=role,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        if role == User.ROLE_STUDENT:
            student = Student(
                name=name,
                student_id=extracted_student_id,
                user_id=user.id,
            )
            db.session.add(student)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User created successfully.",
                    "data": user.to_dict(),
                }
            ),
            201,
        )

    except SQLAlchemyError:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Something went wrong while creating user.",
                }
            ),
            500,
        )


@user_api_bp.route("", methods=["GET"])
@login_required
@admin_required
def list_users():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = User.query.order_by(User.username.asc())
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.role.ilike(f"%{search}%"))
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
                "data": [user.to_dict() for user in pagination.items],
            }
        ),
        200,
    )


@user_api_bp.route("/<int:user_id>", methods=["GET"])
@login_required
@admin_required
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found."}), 404
    return jsonify({"success": True, "data": user.to_dict()}), 200


@user_api_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found."}), 404

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

    error = validate_user_payload(data, partial=True)
    if error:
        return jsonify({"success": False, "error": error}), 400

    if "username" in data:
        normalized_username = normalize_text(data["username"])
        existing_username = User.query.filter_by(username=normalized_username).first()
        if existing_username and existing_username.id != user.id:
            return jsonify({"success": False, "error": "Username already exists."}), 409
        data["username"] = normalized_username

    if "email" in data:
        normalized_email = normalize_email(data["email"])

        existing_email = User.query.filter_by(email=normalized_email).first()
        if existing_email and existing_email.id != user.id:
            return jsonify({"success": False, "error": "Email already exists."}), 409

        if not is_valid_email(normalized_email):
            return jsonify({"success": False, "error": "Email is not valid."}), 400

        data["email"] = normalized_email

    try:
        updated_user = update_user(user, data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "User updated successfully.",
                    "data": updated_user.to_dict(),
                }
            ),
            200,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error occurred."}), 500


@user_api_bp.route("/<int:user_id>", methods=["DELETE"])
@login_required
@admin_required
def remove_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found."}), 404

    if user.id == current_user.id:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "You cannot delete your own admin account.",
                }
            ),
            400,
        )

    delete_user(user)
    return "", 204
