from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.student import Student
from app.models.user import User
from app.utils.file_helpers import save_profile_picture
from app.utils.validators import (
    normalize_email,
    normalize_text,
    validate_login_form,
    validate_register_form,
)

auth_bp = Blueprint("auth_bp", __name__)


def detect_role_and_student_id(email):
    """
    Rules:
    - s12112458@stu.najah.edu -> student, student_id=12112458
    - anything@najah.edu -> instructor
    """
    email = email.strip().lower()

    if email.endswith("@stu.najah.edu"):
        local_part = email.split("@")[0]

        if not local_part.startswith("s") or not local_part[1:].isdigit():
            return None, None, "Invalid student email format."

        student_id = local_part[1:]
        return User.ROLE_STUDENT, student_id, None

    if email.endswith("@najah.edu"):
        return User.ROLE_INSTRUCTOR, None, None

    return None, None, "Please use a valid An-Najah email address."


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))

    if request.method == "POST":
        name = normalize_text(request.form.get("name", ""))
        username = normalize_text(request.form.get("username", ""))
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = validate_register_form(username, email, password, confirm_password)
        if error:
            flash(error, "error")
            return render_template("register.html")

        if not name:
            flash("Full name is required.", "error")
            return render_template("register.html")

        role, extracted_student_id, role_error = detect_role_and_student_id(email)
        if role_error:
            flash(role_error, "error")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username or email already exists.", "error")
            return render_template("register.html")

        if role == User.ROLE_STUDENT:
            existing_student = Student.query.filter_by(
                student_id=extracted_student_id
            ).first()
            if existing_student:
                flash("Student ID already exists.", "error")
                return render_template("register.html")

        profile_picture_file = request.files.get("profile_picture")
        profile_picture = save_profile_picture(
            profile_picture_file,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )

        user = User(
            username=username,
            email=email,
            role=role,
            profile_picture=profile_picture,
        )
        user.set_password(password)

        try:
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

        if user.is_student:
            return redirect(url_for("main_bp.home"))

        return redirect(url_for("main_bp.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth_bp.login"))
