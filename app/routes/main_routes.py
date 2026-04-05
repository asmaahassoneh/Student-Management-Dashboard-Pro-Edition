from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.services.dashboard_service import get_dashboard_stats
from app.services.service_exceptions import PermissionDeniedError

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        stats = get_dashboard_stats(current_user)
        return render_template("dashboard.html", stats=stats, user=current_user)
    except PermissionDeniedError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main_bp.home"))
