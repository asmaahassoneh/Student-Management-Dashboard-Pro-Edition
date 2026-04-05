from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_by_id,
    update_user,
)
from app.utils.decorators import admin_required
from app.utils.validators import normalize_email, normalize_text, validate_user_payload

user_api_bp = Blueprint("user_api_bp", __name__, url_prefix="/api/users")


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


@user_api_bp.route("", methods=["POST"])
@login_required
@admin_required
def add_user():
    data = request.get_json(silent=True)

    error = validate_user_payload(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    existing_username = User.query.filter_by(
        username=normalize_text(data["username"])
    ).first()
    if existing_username:
        return jsonify({"success": False, "error": "Username already exists."}), 409

    existing_email = User.query.filter_by(email=normalize_email(data["email"])).first()
    if existing_email:
        return jsonify({"success": False, "error": "Email already exists."}), 409

    try:
        user = create_user(data)
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
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database integrity error."}), 400


@user_api_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found."}), 404

    data = request.get_json(silent=True)
    error = validate_user_payload(data, partial=True)
    if error:
        return jsonify({"success": False, "error": error}), 400

    if "username" in data:
        existing_username = User.query.filter_by(
            username=normalize_text(data["username"])
        ).first()
        if existing_username and existing_username.id != user.id:
            return jsonify({"success": False, "error": "Username already exists."}), 409

    if "email" in data:
        existing_email = User.query.filter_by(
            email=normalize_email(data["email"])
        ).first()
        if existing_email and existing_email.id != user.id:
            return jsonify({"success": False, "error": "Email already exists."}), 409

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
                {"success": False, "error": "You cannot delete your own admin account."}
            ),
            400,
        )

    delete_user(user)
    return "", 204
