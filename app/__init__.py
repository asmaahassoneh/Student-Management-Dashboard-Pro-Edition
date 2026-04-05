from flask import Flask, jsonify, redirect, render_template, request, url_for, flash

from app.config import Config
from app.extensions import db, login_manager
from app.models.user import User
from app.routes.auth_routes import auth_bp
from app.routes.course_api_routes import course_api_bp
from app.routes.course_page_routes import course_page_bp
from app.routes.main_routes import main_bp
from app.routes.student_api_routes import student_api_bp
from app.routes.student_page_routes import student_page_bp
from app.routes.user_api_routes import user_api_bp
from app.routes.user_page_routes import user_page_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Authentication required."}), 401

        flash(login_manager.login_message, login_manager.login_message_category)
        return redirect(url_for("auth_bp.login"))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_page_bp)
    app.register_blueprint(course_page_bp)
    app.register_blueprint(student_api_bp)
    app.register_blueprint(course_api_bp)
    app.register_blueprint(user_page_bp)
    app.register_blueprint(user_api_bp)

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Resource not found."}), 404
        return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Method not allowed."}), 405
        return render_template("404.html"), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Internal server error."}), 500
        return render_template("404.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Access denied."}), 403
        return render_template("403.html"), 403

    with app.app_context():
        db.create_all()

        admin_email = "admin@gmail.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(
                username="admin",
                email=admin_email,
                role=User.ROLE_ADMIN,
            )
            admin.set_password("Admin1234")
            db.session.add(admin)
            db.session.commit()

    return app
