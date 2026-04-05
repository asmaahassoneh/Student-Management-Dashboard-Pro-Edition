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
from app.services.course_service import (
    create_course,
    delete_course,
    get_course_by_id,
    update_course,
)
from app.utils.decorators import admin_or_instructor_required
from app.utils.validators import normalize_course_code, validate_course_form

course_page_bp = Blueprint("course_page_bp", __name__, url_prefix="/courses")


@course_page_bp.route("")
@login_required
def list_courses():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["COURSES_PER_PAGE"]

    query = Course.query.order_by(Course.name.asc())

    if search:
        query = query.filter(
            (Course.name.ilike(f"%{search}%")) | (Course.code.ilike(f"%{search}%"))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "courses.html", courses=pagination.items, pagination=pagination, search=search
    )


@course_page_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def add_course():
    form_data = {"name": "", "code": "", "description": ""}

    if request.method == "GET":
        return render_template("add_course.html", error=None, form_data=form_data)

    form_data = {
        "name": request.form.get("name", "").strip(),
        "code": request.form.get("code", "").strip(),
        "description": request.form.get("description", "").strip(),
    }

    error = validate_course_form(form_data["name"], form_data["code"])
    if error:
        return render_template("add_course.html", error=error, form_data=form_data)

    normalized_code = normalize_course_code(form_data["code"])

    existing_name = Course.query.filter_by(name=form_data["name"]).first()
    if existing_name:
        return render_template(
            "add_course.html", error="Course name already exists.", form_data=form_data
        )

    existing_code = Course.query.filter_by(code=normalized_code).first()
    if existing_code:
        return render_template(
            "add_course.html", error="Course code already exists.", form_data=form_data
        )

    try:
        create_course(form_data)
        flash("Course added successfully.", "success")
        return redirect(url_for("course_page_bp.list_courses"))
    except SQLAlchemyError:
        return render_template(
            "add_course.html", error="Database error occurred.", form_data=form_data
        )


@course_page_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def edit_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        abort(404)

    if request.method == "GET":
        return render_template("edit_course.html", course=course, error=None)

    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    description = request.form.get("description", "").strip()

    error = validate_course_form(name, code)
    if error:
        return render_template("edit_course.html", course=course, error=error)

    normalized_code = normalize_course_code(code)

    existing_name = Course.query.filter_by(name=name).first()
    if existing_name and existing_name.id != course.id:
        return render_template(
            "edit_course.html", course=course, error="Course name already exists."
        )

    existing_code = Course.query.filter_by(code=normalized_code).first()
    if existing_code and existing_code.id != course.id:
        return render_template(
            "edit_course.html", course=course, error="Course code already exists."
        )

    data = {"name": name, "code": code, "description": description}

    try:
        update_course(course, data)
        flash("Course updated successfully.", "success")
        return redirect(url_for("course_page_bp.list_courses"))
    except SQLAlchemyError:
        return render_template(
            "edit_course.html", course=course, error="Database error occurred."
        )


@course_page_bp.route("/<int:course_id>/delete", methods=["POST"])
@login_required
@admin_or_instructor_required
def remove_course(course_id):
    course = get_course_by_id(course_id)
    if course is None:
        abort(404)

    try:
        delete_course(course)
        flash("Course deleted successfully.", "success")
    except SQLAlchemyError:
        flash("Something went wrong while deleting the course.", "error")

    return redirect(url_for("course_page_bp.list_courses"))
