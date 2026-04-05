from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.services.auth_service import (
    authenticate_user,
    logout_current_user,
    register_user,
)
from app.services.service_exceptions import ConflictError, ValidationError

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))

    if request.method == "POST":
        try:
            register_user(
                request.form,
                request.files,
                current_app.config["UPLOAD_FOLDER"],
                current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
            )
            flash("Registration successful. You can now log in.", "success")
            return redirect(url_for("auth_bp.login"))
        except (ValidationError, ConflictError) as exc:
            flash(str(exc), "error")
            return render_template("register.html")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))

    if request.method == "POST":
        try:
            user = authenticate_user(request.form)
            flash("Login successful.", "success")

            if user.is_student:
                return redirect(url_for("main_bp.home"))

            return redirect(url_for("main_bp.dashboard"))
        except ValidationError as exc:
            flash(str(exc), "error")
            return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_current_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth_bp.login"))
