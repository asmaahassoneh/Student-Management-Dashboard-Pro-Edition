from functools import wraps

from flask import abort, jsonify, request
from flask_login import current_user


def roles_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith("/api/"):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Authentication required.",
                            }
                        ),
                        401,
                    )
                abort(401)

            if current_user.role not in allowed_roles:
                if request.path.startswith("/api/"):
                    if "admin" in allowed_roles:
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": "Admin access required.",
                                }
                            ),
                            403,
                        )

                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Access denied.",
                            }
                        ),
                        403,
                    )
                abort(403)

            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(view_func):
    return roles_required("admin")(view_func)


def admin_or_instructor_required(view_func):
    return roles_required("admin", "instructor")(view_func)
