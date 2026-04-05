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
    PermissionDeniedError,
    ValidationError,
)
from app.services.student_service import (
    create_student_with_user,
    delete_student,
    ensure_student_access,
    get_all_courses_for_forms,
    get_student_courses_for_current_user,
    paginate_students,
    require_student,
    update_student,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import validate_student_form

student_page_bp = Blueprint("student_page_bp", __name__, url_prefix="/students")


@student_page_bp.route("")
@login_required
def list_students():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["STUDENTS_PER_PAGE"]

    pagination = paginate_students(search=search, page=page, per_page=per_page)

    return render_template(
        "students.html",
        students=pagination.items,
        pagination=pagination,
        search=search,
    )


@student_page_bp.route("/my-courses")
@login_required
def my_courses():
    try:
        student = get_student_courses_for_current_user(current_user)
        return render_template("my_courses.html", student=student)
    except PermissionDeniedError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main_bp.dashboard"))
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main_bp.home"))


@student_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def add_student():
    courses = get_all_courses_for_forms()

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

    try:
        user, student = create_student_with_user(form_data, password, confirm_password)
        flash(f"Student added successfully. Login email: {user.email}", "success")
        return redirect(
            url_for("student_page_bp.student_details", student_id=student.student_id)
        )
    except (ValidationError, ConflictError) as exc:
        return render_template(
            "add_student.html",
            error=str(exc),
            form_data=form_data,
            courses=courses,
        )


@student_page_bp.route("/<student_id>")
@login_required
def student_details(student_id):
    try:
        student = require_student(student_id)
        ensure_student_access(current_user, student)
        return render_template("student_details.html", student=student)
    except NotFoundError:
        abort(404)
    except PermissionDeniedError:
        abort(403)
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main_bp.home"))


@student_page_bp.route("/<student_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def edit_student(student_id):
    try:
        student = require_student(student_id)
    except NotFoundError:
        abort(404)

    courses = get_all_courses_for_forms()

    if request.method == "GET":
        return render_template(
            "edit_student.html",
            student=student,
            courses=courses,
            error=None,
        )

    name = request.form.get("name", "").strip()
    selected_course_ids = request.form.getlist("course_ids")

    error = validate_student_form(name, student.student_id, selected_course_ids)
    if error:
        return render_template(
            "edit_student.html",
            student=student,
            courses=courses,
            error=error,
        )

    try:
        from app.services.student_service import get_courses_by_ids

        selected_courses = get_courses_by_ids(selected_course_ids)
        update_student(student, {"name": name}, selected_courses)
        flash("Student updated successfully.", "success")
        return redirect(
            url_for("student_page_bp.student_details", student_id=student.student_id)
        )
    except ValidationError as exc:
        return render_template(
            "edit_student.html",
            student=student,
            courses=courses,
            error=str(exc),
        )


@student_page_bp.route("/<student_id>/delete", methods=["POST"])
@login_required
@admin_or_instructor_required
def remove_student(student_id):
    try:
        student = require_student(student_id)
        delete_student(student)
        flash("Student deleted successfully.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as exc:
        flash(str(exc), "error")

    return redirect(url_for("student_page_bp.list_students"))
