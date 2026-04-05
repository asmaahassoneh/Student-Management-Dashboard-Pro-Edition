from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.course import Course
from app.models.student import Student
from app.models.user import User

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "students_count": Student.query.count(),
        "courses_count": Course.query.count(),
        "users_count": User.query.count(),
    }
    return render_template("dashboard.html", stats=stats, user=current_user)
