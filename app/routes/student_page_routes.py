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

from app.extensions import db
from app.models.course import Course
from app.models.student import Student
from app.models.user import User
from app.services.student_service import (
    delete_student,
    get_courses_by_ids,
    get_student_by_student_id,
    update_student,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import (
    normalize_email,
    normalize_text,
    validate_student_form,
    validate_user_form,
)
from app.utils.role_helpers import extract_student_id

student_page_bp = Blueprint("student_page_bp", __name__, url_prefix="/students")


@student_page_bp.route("")
@login_required
def list_students():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["STUDENTS_PER_PAGE"]

    query = Student.query.order_by(Student.name.asc())

    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%"))
            | (Student.student_id.ilike(f"%{search}%"))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "students.html",
        students=pagination.items,
        pagination=pagination,
        search=search,
    )


@student_page_bp.route("/my-courses")
@login_required
def my_courses():
    if not current_user.is_student:
        flash("This page is only available for student accounts.", "error")
        return redirect(url_for("main_bp.dashboard"))

    student = current_user.student_profile
    if student is None:
        flash("No student profile is linked to this account.", "error")
        return redirect(url_for("main_bp.home"))

    return render_template("my_courses.html", student=student)


@student_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def add_student():
    courses = Course.query.order_by(Course.name.asc()).all()

    form_data = {
        "name": "",
        "username": "",
        "email": "",
        "course_ids": [],
    }

    if request.method == "GET":
        return render_template(
            "add_student.html",
            error=None,
            form_data=form_data,
            courses=courses,
        )

    form_data = {
        "name": request.form.get("name", "").strip(),
        "username": request.form.get("username", "").strip(),
        "email": request.form.get("email", "").strip(),
        "course_ids": request.form.getlist("course_ids"),
    }

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    error = validate_student_form(
        form_data["name"], "12345678", form_data["course_ids"]
    )
    if error and "Student ID" not in error:
        return render_template(
            "add_student.html",
            error=error,
            form_data=form_data,
            courses=courses,
        )

    user_error = validate_user_form(
        form_data["username"],
        form_data["email"],
        password,
        confirm_password,
        role=User.ROLE_STUDENT,
    )
    if user_error:
        return render_template(
            "add_student.html",
            error=user_error,
            form_data=form_data,
            courses=courses,
        )

    student_id = extract_student_id(form_data["email"])
    if not student_id:
        return render_template(
            "add_student.html",
            error="Student email must be in this format: sXXXXXXXX@stu.najah.edu",
            form_data=form_data,
            courses=courses,
        )

    existing_student_id = Student.query.filter_by(student_id=student_id).first()
    if existing_student_id:
        return render_template(
            "add_student.html",
            error="Student ID already exists.",
            form_data=form_data,
            courses=courses,
        )

    existing_username = User.query.filter_by(
        username=normalize_text(form_data["username"])
    ).first()
    if existing_username:
        return render_template(
            "add_student.html",
            error="Username already exists.",
            form_data=form_data,
            courses=courses,
        )

    existing_email = User.query.filter_by(
        email=normalize_email(form_data["email"])
    ).first()
    if existing_email:
        return render_template(
            "add_student.html",
            error="Email already exists.",
            form_data=form_data,
            courses=courses,
        )

    selected_courses = get_courses_by_ids(form_data["course_ids"])

    try:
        user = User(
            username=normalize_text(form_data["username"]),
            email=normalize_email(form_data["email"]),
            role=User.ROLE_STUDENT,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        student = Student(
            name=normalize_text(form_data["name"]),
            student_id=student_id,
            user_id=user.id,
        )
        student.courses = selected_courses

        db.session.add(student)
        db.session.commit()

        flash(
            f"Student added successfully. Login email: {user.email}",
            "success",
        )
        return redirect(
            url_for("student_page_bp.student_details", student_id=student.student_id)
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash("Something went wrong while saving the student.", "error")
        return render_template(
            "add_student.html",
            error="Database error occurred.",
            form_data=form_data,
            courses=courses,
        )


@student_page_bp.route("/<student_id>")
@login_required
def student_details(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        abort(404)

    if current_user.is_student:
        if current_user.student_profile is None:
            flash("No student profile is linked to this account.", "error")
            return redirect(url_for("main_bp.home"))

        if current_user.student_profile.student_id != student.student_id:
            abort(403)

    return render_template("student_details.html", student=student)


@student_page_bp.route("/<student_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def edit_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        abort(404)

    courses = Course.query.order_by(Course.name.asc()).all()

    if request.method == "GET":
        return render_template(
            "edit_student.html", student=student, courses=courses, error=None
        )

    name = request.form.get("name", "").strip()
    selected_course_ids = request.form.getlist("course_ids")

    error = validate_student_form(name, student.student_id, selected_course_ids)
    if error:
        return render_template(
            "edit_student.html", student=student, courses=courses, error=error
        )

    selected_courses = get_courses_by_ids(selected_course_ids)

    data = {"name": name}

    try:
        update_student(student, data, selected_courses)
        flash("Student updated successfully.", "success")
        return redirect(
            url_for("student_page_bp.student_details", student_id=student.student_id)
        )
    except SQLAlchemyError:
        return render_template(
            "edit_student.html",
            student=student,
            courses=courses,
            error="Database error occurred.",
        )


@student_page_bp.route("/<student_id>/delete", methods=["POST"])
@login_required
@admin_or_instructor_required
def remove_student(student_id):
    student = get_student_by_student_id(student_id)
    if student is None:
        abort(404)

    try:
        delete_student(student)
        flash("Student deleted successfully.", "success")
    except SQLAlchemyError:
        flash("Something went wrong while deleting the student.", "error")

    return redirect(url_for("student_page_bp.list_students"))
