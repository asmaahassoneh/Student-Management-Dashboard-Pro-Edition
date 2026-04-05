from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.services.user_service import (
    create_user,
    delete_user,
    paginate_users,
    require_user,
    update_user,
    validate_user_api_create,
    validate_user_api_update,
)
from app.utils.decorators import admin_required

user_api_bp = Blueprint("user_api_bp", __name__, url_prefix="/api/users")


@user_api_bp.route("", methods=["POST"])
@login_required
@admin_required
def create_user_route():
    try:
        clean_data = validate_user_api_create(request.get_json(silent=True))
        user = create_user(clean_data)
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
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@user_api_bp.route("", methods=["GET"])
@login_required
@admin_required
def list_users():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = paginate_users(search=search, page=page, per_page=per_page)

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
    try:
        user = require_user(user_id)
        return jsonify({"success": True, "data": user.to_dict()}), 200
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404


@user_api_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
@admin_required
def edit_user(user_id):
    try:
        user = require_user(user_id)
        clean_data = validate_user_api_update(user, request.get_json(silent=True))
        updated_user = update_user(user, clean_data)
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
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except ConflictError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409


@user_api_bp.route("/<int:user_id>", methods=["DELETE"])
@login_required
@admin_required
def remove_user(user_id):
    try:
        user = require_user(user_id)

        if user.id == current_user.id:
            raise ValidationError("You cannot delete your own admin account.")

        delete_user(user)
        return "", 204
    except NotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
