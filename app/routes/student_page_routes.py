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
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from app.models.course import Course
from app.models.student import Student
from app.services.student_service import (
    create_student,
    delete_student,
    get_courses_by_ids,
    get_student_by_student_id,
    update_student,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import normalize_student_id, validate_student_form

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


@student_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def add_student():
    courses = Course.query.order_by(Course.name.asc()).all()

    form_data = {"name": "", "student_id": "", "course_ids": []}

    if request.method == "GET":
        return render_template(
            "add_student.html", error=None, form_data=form_data, courses=courses
        )

    form_data = {
        "name": request.form.get("name", "").strip(),
        "student_id": request.form.get("student_id", "").strip(),
        "course_ids": request.form.getlist("course_ids"),
    }

    error = validate_student_form(
        form_data["name"], form_data["student_id"], form_data["course_ids"]
    )
    if error:
        return render_template(
            "add_student.html", error=error, form_data=form_data, courses=courses
        )

    normalized_student_id = normalize_student_id(form_data["student_id"])
    existing_student_id = Student.query.filter_by(
        student_id=normalized_student_id
    ).first()
    if existing_student_id:
        return render_template(
            "add_student.html",
            error="Student ID already exists.",
            form_data=form_data,
            courses=courses,
        )

    selected_courses = get_courses_by_ids(form_data["course_ids"])
    if not selected_courses:
        return render_template(
            "add_student.html",
            error="Please select valid courses.",
            form_data=form_data,
            courses=courses,
        )

    try:
        student = create_student(form_data, selected_courses)
        flash("Student added successfully.", "success")
        return redirect(
            url_for("student_page_bp.student_details", student_id=student.student_id)
        )
    except SQLAlchemyError:
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
    if not selected_courses:
        return render_template(
            "edit_student.html",
            student=student,
            courses=courses,
            error="Please select valid courses.",
        )

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
