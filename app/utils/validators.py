import re

from app.models.user import User


def normalize_text(value):
    return value.strip() if isinstance(value, str) else value


def normalize_email(email):
    return email.strip().lower() if isinstance(email, str) else email


def normalize_student_id(student_id):
    return student_id.strip().upper() if isinstance(student_id, str) else student_id


def normalize_course_code(code):
    return code.strip().upper() if isinstance(code, str) else code


def is_valid_email(email):
    if not isinstance(email, str):
        return False
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(pattern, email) is not None


def is_strong_password(password):
    if not isinstance(password, str):
        return False
    if len(password) < 8:
        return False

    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)

    return has_letter and has_digit


def validate_register_form(username, email, password, confirm_password):
    username = normalize_text(username)
    email = normalize_email(email)

    if not username or not email or not password or not confirm_password:
        return "All fields are required."

    if not is_valid_email(email):
        return "Email is not valid."

    if password != confirm_password:
        return "Passwords do not match."

    if not is_strong_password(password):
        return "Password must be at least 8 characters long and include both letters and numbers."

    return None


def validate_login_form(email, password):
    email = normalize_email(email)

    if not email or not password:
        return "Email and password are required."

    if not is_valid_email(email):
        return "Email is not valid."

    return None


def validate_student_form(name, student_id, course_ids=None):
    name = normalize_text(name)
    student_id = normalize_student_id(student_id)

    if not name or not student_id:
        return "All fields are required."

    if not student_id.isalnum():
        return "Student ID must contain only letters and numbers."

    if course_ids is not None and not course_ids:
        return "Select at least one course."

    return None


def validate_course_form(name, code):
    name = normalize_text(name)
    code = normalize_course_code(code)

    if not name or not code:
        return "Course name and code are required."

    if not code.replace("-", "").isalnum():
        return "Course code must contain only letters, numbers, or dashes."

    return None


def validate_role(role):
    if role not in User.ROLES:
        return f"Role must be one of: {', '.join(User.ROLES)}."
    return None


def validate_user_form(
    username, email, password=None, confirm_password=None, partial=False, role=None
):
    username = normalize_text(username)
    email = normalize_email(email)

    if not partial:
        if not username or not email:
            return "Username and email are required."

        if password is not None and confirm_password is not None:
            if not password or not confirm_password:
                return "All fields are required."

            if password != confirm_password:
                return "Passwords do not match."

            if not is_strong_password(password):
                return "Password must be at least 8 characters long and include both letters and numbers."

    if email and not is_valid_email(email):
        return "Email is not valid."

    if password and not is_strong_password(password):
        return "Password must be at least 8 characters long and include both letters and numbers."

    if role is not None:
        role_error = validate_role(role)
        if role_error:
            return role_error

    return None


def validate_student_payload(data, partial=False):
    required_fields = ["name", "student_id"]

    if not isinstance(data, dict):
        return "Request body must be valid JSON."

    if not partial:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}."

    if "name" in data and not normalize_text(data.get("name")):
        return "Name is required."

    if "student_id" in data:
        student_id = normalize_student_id(data.get("student_id"))
        if not student_id:
            return "Student ID is required."
        if not student_id.isalnum():
            return "Student ID must contain only letters and numbers."

    return None


def validate_course_payload(data, partial=False):
    required_fields = ["name", "code"]

    if not isinstance(data, dict):
        return "Request body must be valid JSON."

    if not partial:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}."

    if "name" in data and not normalize_text(data.get("name")):
        return "Course name is required."

    if "code" in data:
        code = normalize_course_code(data.get("code"))
        if not code:
            return "Course code is required."
        if not code.replace("-", "").isalnum():
            return "Course code must contain only letters, numbers, or dashes."

    return None


def validate_user_payload(data, partial=False):
    required_fields = ["username", "email", "password", "role"]

    if not isinstance(data, dict):
        return "Request body must be valid JSON."

    if not partial:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}."

    if "username" in data and not normalize_text(data.get("username")):
        return "Username is required."

    if "email" in data:
        email = normalize_email(data.get("email"))
        if not email:
            return "Email is required."
        if not is_valid_email(email):
            return "Email is not valid."

    if not partial and "password" in data:
        password = data.get("password")
        if not password:
            return "Password is required."
        if not is_strong_password(password):
            return "Password must be at least 8 characters long and include both letters and numbers."

    if partial and "password" in data and data.get("password"):
        if not is_strong_password(data["password"]):
            return "Password must be at least 8 characters long and include both letters and numbers."

    if "role" in data:
        role_error = validate_role(data["role"])
        if role_error:
            return role_error

    return None
