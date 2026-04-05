from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_by_id,
    update_user,
)
from app.utils.decorators import admin_required
from app.utils.file_helpers import save_profile_picture
from app.utils.validators import normalize_email, normalize_text, validate_user_form

user_page_bp = Blueprint("user_page_bp", __name__, url_prefix="/users")


@user_page_bp.route("")
@login_required
@admin_required
def list_users():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["USERS_PER_PAGE"]

    query = User.query.order_by(User.username.asc())
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.role.ilike(f"%{search}%"))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "users.html", users=pagination.items, pagination=pagination, search=search
    )


@user_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    form_data = {"username": "", "email": "", "role": User.ROLE_STUDENT}

    if request.method == "GET":
        return render_template(
            "add_user.html", error=None, form_data=form_data, roles=User.ROLES
        )

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    role = request.form.get("role", User.ROLE_STUDENT)

    profile_picture_file = request.files.get("profile_picture")
    profile_picture = save_profile_picture(
        profile_picture_file,
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
    )

    form_data = {"username": username, "email": email, "role": role}

    error = validate_user_form(username, email, password, confirm_password, role=role)
    if error:
        return render_template(
            "add_user.html", error=error, form_data=form_data, roles=User.ROLES
        )

    existing_username = User.query.filter_by(username=normalize_text(username)).first()
    if existing_username:
        return render_template(
            "add_user.html",
            error="Username already exists.",
            form_data=form_data,
            roles=User.ROLES,
        )

    existing_email = User.query.filter_by(email=normalize_email(email)).first()
    if existing_email:
        return render_template(
            "add_user.html",
            error="Email already exists.",
            form_data=form_data,
            roles=User.ROLES,
        )

    try:
        create_user(
            {
                "username": username,
                "email": email,
                "password": password,
                "role": role,
                "profile_picture": profile_picture,
            }
        )
        flash("User added successfully.", "success")
        return redirect(url_for("user_page_bp.list_users"))
    except SQLAlchemyError:
        return render_template(
            "add_user.html",
            error="Database error occurred.",
            form_data=form_data,
            roles=User.ROLES,
        )


@user_page_bp.route("/<int:user_id>")
@login_required
@admin_required
def user_details(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)
    return render_template("user_details.html", user=user)


@user_page_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)

    if request.method == "GET":
        return render_template(
            "edit_user.html", user=user, error=None, roles=User.ROLES
        )

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", user.role)

    profile_picture_file = request.files.get("profile_picture")
    profile_picture = None
    if profile_picture_file and profile_picture_file.filename:
        profile_picture = save_profile_picture(
            profile_picture_file,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )

    error = validate_user_form(
        username, email, password=password, partial=True, role=role
    )
    if error:
        return render_template(
            "edit_user.html", user=user, error=error, roles=User.ROLES
        )

    existing_username = User.query.filter_by(username=normalize_text(username)).first()
    if existing_username and existing_username.id != user.id:
        return render_template(
            "edit_user.html",
            user=user,
            error="Username already exists.",
            roles=User.ROLES,
        )

    existing_email = User.query.filter_by(email=normalize_email(email)).first()
    if existing_email and existing_email.id != user.id:
        return render_template(
            "edit_user.html", user=user, error="Email already exists.", roles=User.ROLES
        )

    data = {"username": username, "email": email, "role": role}
    if password:
        data["password"] = password
    if profile_picture:
        data["profile_picture"] = profile_picture

    try:
        update_user(user, data)
        flash("User updated successfully.", "success")
        return redirect(url_for("user_page_bp.user_details", user_id=user.id))
    except SQLAlchemyError:
        return render_template(
            "edit_user.html",
            user=user,
            error="Database error occurred.",
            roles=User.ROLES,
        )


@user_page_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def remove_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)

    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", "error")
        return redirect(url_for("user_page_bp.list_users"))

    try:
        delete_user(user)
        flash("User deleted successfully.", "success")
    except SQLAlchemyError:
        flash("Something went wrong while deleting the user.", "error")

    return redirect(url_for("user_page_bp.list_users"))
