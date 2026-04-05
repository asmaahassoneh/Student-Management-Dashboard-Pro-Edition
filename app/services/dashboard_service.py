from app.models.course import Course
from app.models.student import Student
from app.models.user import User
from app.services.service_exceptions import PermissionDeniedError


def get_dashboard_stats(current_user):
    if current_user.is_student:
        raise PermissionDeniedError(
            "Students do not have access to the management dashboard."
        )

    return {
        "students_count": Student.query.count(),
        "courses_count": Course.query.count(),
        "users_count": User.query.count(),
    }
