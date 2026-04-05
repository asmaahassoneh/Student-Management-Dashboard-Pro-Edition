from app.models.user import User


def detect_role_and_student_id(email: str):
    email = (email or "").strip().lower()

    if email.endswith("@stu.najah.edu"):
        local_part = email.split("@")[0]

        if not local_part.startswith("s") or not local_part[1:].isdigit():
            return None, None, "Invalid student email format."

        return User.ROLE_STUDENT, local_part[1:], None

    if email.endswith("@najah.edu"):
        return User.ROLE_INSTRUCTOR, None, None

    return None, None, "Please use a valid An-Najah email address."


def extract_student_id(email: str):
    email = (email or "").strip().lower()

    if not email.endswith("@stu.najah.edu"):
        return None

    local_part = email.split("@")[0]

    if not local_part.startswith("s") or not local_part[1:].isdigit():
        return None

    return local_part[1:]
