from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.user import User
from app.utils.file_helpers import save_profile_picture
from app.utils.validators import (
    normalize_email,
    normalize_text,
    validate_login_form,
    validate_register_form,
)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))

    if request.method == "POST":
        username = normalize_text(request.form.get("username", ""))
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = validate_register_form(username, email, password, confirm_password)
        if error:
            flash(error, "error")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.", "error")
            return render_template("register.html")

        profile_picture_file = request.files.get("profile_picture")
        profile_picture = save_profile_picture(
            profile_picture_file,
            str(auth_bp.root_path.rsplit("app", 1)[0] + "app/static/uploads"),
            {"png", "jpg", "jpeg", "gif"},
        )

        user = User(
            username=username,
            email=email,
            role=User.ROLE_STUDENT,
            profile_picture=profile_picture,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Something went wrong while creating your account.", "error")
            return render_template("register.html"), 500

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))

    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        error = validate_login_form(email, password)
        if error:
            flash(error, "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        login_user(user)
        flash("Login successful.", "success")
        return redirect(url_for("main_bp.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth_bp.login"))
