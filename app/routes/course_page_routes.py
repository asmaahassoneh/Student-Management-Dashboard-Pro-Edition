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
from flask_login import login_required

from app.services.course_service import (
    create_course,
    delete_course,
    paginate_courses,
    require_course,
    update_course,
)
from app.services.service_exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.utils.decorators import admin_or_instructor_required

course_page_bp = Blueprint("course_page_bp", __name__, url_prefix="/courses")


@course_page_bp.route("")
@login_required
def list_courses():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["COURSES_PER_PAGE"]

    pagination = paginate_courses(search=search, page=page, per_page=per_page)
    return render_template(
        "courses.html",
        courses=pagination.items,
        pagination=pagination,
        search=search,
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

    try:
        create_course(form_data)
        flash("Course added successfully.", "success")
        return redirect(url_for("course_page_bp.list_courses"))
    except (ValidationError, ConflictError) as exc:
        return render_template("add_course.html", error=str(exc), form_data=form_data)


@course_page_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_instructor_required
def edit_course(course_id):
    try:
        course = require_course(course_id)
    except NotFoundError:
        abort(404)

    if request.method == "GET":
        return render_template("edit_course.html", course=course, error=None)

    data = {
        "name": request.form.get("name", "").strip(),
        "code": request.form.get("code", "").strip(),
        "description": request.form.get("description", "").strip(),
    }

    try:
        update_course(course, data)
        flash("Course updated successfully.", "success")
        return redirect(url_for("course_page_bp.list_courses"))
    except (ValidationError, ConflictError) as exc:
        return render_template("edit_course.html", course=course, error=str(exc))


@course_page_bp.route("/<int:course_id>/delete", methods=["POST"])
@login_required
@admin_or_instructor_required
def remove_course(course_id):
    try:
        course = require_course(course_id)
        delete_course(course)
        flash("Course deleted successfully.", "success")
    except NotFoundError:
        abort(404)
    except ValidationError as exc:
        flash(str(exc), "error")

    return redirect(url_for("course_page_bp.list_courses"))
