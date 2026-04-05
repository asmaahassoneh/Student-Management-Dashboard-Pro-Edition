from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.services.user_service import (
    delete_user,
    paginate_users,
    require_user,
    update_user,
    validate_user_page_create,
    validate_user_page_update,
)
from app.utils.decorators import admin_required
from app.utils.file_helpers import save_profile_picture

user_page_bp = Blueprint("user_page_bp", __name__, url_prefix="/users")


@user_page_bp.route("")
@login_required
@admin_required
def list_users():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["USERS_PER_PAGE"]

    pagination = paginate_users(search=search, page=page, per_page=per_page)

    return render_template(
        "users.html",
        users=pagination.items,
        pagination=pagination,
        search=search,
    )


@user_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    form_data = {"username": "", "email": "", "name": ""}

    if request.method == "GET":
        return render_template("add_user.html", error=None, form_data=form_data)

    username = request.form.get("username", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    profile_picture = save_profile_picture(
        request.files.get("profile_picture"),
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
    )

    form_data = {"username": username, "email": email, "name": name}

    try:
        clean_data = validate_user_page_create(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            name=name,
        )
        clean_data["profile_picture"] = profile_picture

        flash("User added successfully.", "success")
        return redirect(url_for("user_page_bp.list_users"))
    except (ValidationError, ConflictError) as exc:
        return render_template(
            "add_user.html",
            error=str(exc),
            form_data=form_data,
        )


@user_page_bp.route("/<int:user_id>")
@login_required
@admin_required
def user_details(user_id):
    try:
        user = require_user(user_id)
        return render_template("user_details.html", user=user)
    except NotFoundError:
        abort(404)


@user_page_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    try:
        user = require_user(user_id)
    except NotFoundError:
        abort(404)

    if request.method == "GET":
        from app.models.user import User

        return render_template(
            "edit_user.html",
            user=user,
            error=None,
            roles=User.ROLES,
        )

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", user.role)

    profile_picture = None
    profile_picture_file = request.files.get("profile_picture")
    if profile_picture_file and profile_picture_file.filename:
        profile_picture = save_profile_picture(
            profile_picture_file,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )

    try:
        clean_data = validate_user_page_update(user, username, email, password, role)
        if profile_picture:
            clean_data["profile_picture"] = profile_picture

        update_user(user, clean_data)
        flash("User updated successfully.", "success")
        return redirect(url_for("user_page_bp.user_details", user_id=user.id))
    except (ValidationError, ConflictError) as exc:
        from app.models.user import User

        return render_template(
            "edit_user.html",
            user=user,
            error=str(exc),
            roles=User.ROLES,
        )


@user_page_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def remove_user(user_id):
    try:
        user = require_user(user_id)

        if user.id == current_user.id:
            raise ValidationError("You cannot delete your own admin account.")

        delete_user(user)
        flash("User deleted successfully.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as exc:
        flash(str(exc), "error")

    return redirect(url_for("user_page_bp.list_users"))
