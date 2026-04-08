import io
import os

from werkzeug.datastructures import FileStorage

from app.utils.file_helpers import allowed_file, save_profile_picture
from app.utils.role_helpers import detect_role_and_student_id, extract_student_id
from app.utils.validators import (
    is_strong_password,
    is_valid_email,
    normalize_course_code,
    normalize_email,
    normalize_student_id,
    normalize_text,
    validate_course_form,
    validate_login_form,
    validate_register_form,
    validate_role,
    validate_student_form,
    validate_user_payload,
)


def test_allowed_file_accepts_valid_extension():
    assert allowed_file("avatar.png", {"png", "jpg", "jpeg"})


def test_allowed_file_rejects_invalid_extension():
    assert not allowed_file("avatar.exe", {"png", "jpg", "jpeg"})


def test_save_profile_picture_returns_none_for_missing_file(tmp_path):
    result = save_profile_picture(None, str(tmp_path), {"png", "jpg"})
    assert result is None


def test_save_profile_picture_returns_none_for_empty_filename(tmp_path):
    file_storage = FileStorage(stream=io.BytesIO(b"abc"), filename="")
    result = save_profile_picture(file_storage, str(tmp_path), {"png", "jpg"})
    assert result is None


def test_save_profile_picture_returns_none_for_invalid_extension(tmp_path):
    file_storage = FileStorage(stream=io.BytesIO(b"abc"), filename="bad.exe")
    result = save_profile_picture(file_storage, str(tmp_path), {"png", "jpg"})
    assert result is None


def test_save_profile_picture_saves_valid_file(tmp_path):
    file_storage = FileStorage(
        stream=io.BytesIO(b"fake-image-content"),
        filename="profile.PNG",
    )
    result = save_profile_picture(file_storage, str(tmp_path), {"png", "jpg", "jpeg"})
    assert result is not None
    assert result.endswith(".png")
    assert os.path.exists(tmp_path / result)


def test_detect_role_and_student_id_student_email():
    role, student_id, error = detect_role_and_student_id("s12110001@stu.najah.edu")
    assert role == "student"
    assert student_id == "12110001"
    assert error is None


def test_detect_role_and_student_id_invalid_student_email():
    role, student_id, error = detect_role_and_student_id("student@stu.najah.edu")
    assert role is None
    assert student_id is None
    assert error == "Invalid student email format."


def test_detect_role_and_student_id_instructor_email():
    role, student_id, error = detect_role_and_student_id("teacher@najah.edu")
    assert role == "instructor"
    assert student_id is None
    assert error is None


def test_detect_role_and_student_id_invalid_domain():
    role, student_id, error = detect_role_and_student_id("teacher@gmail.com")
    assert role is None
    assert student_id is None
    assert error == "Please use a valid An-Najah email address."


def test_extract_student_id_valid():
    assert extract_student_id("s12118888@stu.najah.edu") == "12118888"


def test_extract_student_id_invalid_domain():
    assert extract_student_id("teacher@najah.edu") is None


def test_extract_student_id_invalid_local_part():
    assert extract_student_id("student@stu.najah.edu") is None


def test_normalize_text():
    assert normalize_text("  hello  ") == "hello"


def test_normalize_email():
    assert normalize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"


def test_normalize_student_id():
    assert normalize_student_id("  ab12  ") == "AB12"


def test_normalize_course_code():
    assert normalize_course_code("  cse-201  ") == "CSE-201"


def test_is_valid_email_true():
    assert is_valid_email("user@example.com") is True


def test_is_valid_email_false():
    assert is_valid_email("not-an-email") is False


def test_is_strong_password_true():
    assert is_strong_password("Strong123") is True


def test_is_strong_password_false():
    assert is_strong_password("weak") is False


def test_validate_register_form_success():
    assert (
        validate_register_form(
            "asmaa",
            "asmaa@example.com",
            "Password123",
            "Password123",
        )
        is None
    )


def test_validate_register_form_missing_fields():
    assert (
        validate_register_form("", "asmaa@example.com", "Password123", "Password123")
        == "All fields are required."
    )


def test_validate_register_form_invalid_email():
    assert (
        validate_register_form("asmaa", "bad-email", "Password123", "Password123")
        == "Email is not valid."
    )


def test_validate_register_form_password_mismatch():
    assert (
        validate_register_form(
            "asmaa", "asmaa@example.com", "Password123", "Password456"
        )
        == "Passwords do not match."
    )


def test_validate_register_form_weak_password():
    assert (
        validate_register_form("asmaa", "asmaa@example.com", "weak", "weak")
        == "Password must be at least 8 characters long and include both letters and numbers."
    )


def test_validate_login_form_success():
    assert validate_login_form("user@example.com", "Password123") is None


def test_validate_login_form_missing_fields():
    assert validate_login_form("", "") == "Email and password are required."


def test_validate_login_form_invalid_email():
    assert validate_login_form("bad-email", "Password123") == "Email is not valid."


def test_validate_student_form_success():
    assert validate_student_form("Student Name", "12110001", ["1"]) is None


def test_validate_student_form_missing_fields():
    assert validate_student_form("", "", ["1"]) == "All fields are required."


def test_validate_student_form_invalid_student_id():
    assert (
        validate_student_form("Student Name", "12-110001", ["1"])
        == "Student ID must contain only letters and numbers."
    )


def test_validate_student_form_requires_course_selection():
    assert (
        validate_student_form("Student Name", "12110001", [])
        == "Select at least one course."
    )


def test_validate_course_form_success():
    assert validate_course_form("Databases", "CSE302") is None


def test_validate_course_form_missing_fields():
    assert validate_course_form("", "") == "Course name and code are required."


def test_validate_course_form_invalid_code():
    assert (
        validate_course_form("Databases", "CSE 302!")
        == "Course code must contain only letters, numbers, or dashes."
    )


def test_validate_role_success():
    assert validate_role("admin") is None


def test_validate_role_invalid():
    assert (
        validate_role("manager") == "Role must be one of: admin, instructor, student."
    )


def test_validate_user_payload_non_dict():
    assert (
        validate_user_payload(None, partial=False) == "Request body must be valid JSON."
    )


def test_validate_user_payload_missing_required_fields():
    assert (
        validate_user_payload({"username": "asmaa"}, partial=False)
        == "Missing required fields: email, password, role."
    )


def test_validate_user_payload_blank_username():
    payload = {
        "username": "   ",
        "email": "asmaa@example.com",
        "password": "Password123",
        "role": "student",
    }
    assert validate_user_payload(payload, partial=False) == "Username is required."


def test_validate_user_payload_blank_email():
    payload = {
        "username": "asmaa",
        "email": "   ",
        "password": "Password123",
        "role": "student",
    }
    assert validate_user_payload(payload, partial=False) == "Email is required."


def test_validate_user_payload_invalid_email():
    payload = {
        "username": "asmaa",
        "email": "bad-email",
        "password": "Password123",
        "role": "student",
    }
    assert validate_user_payload(payload, partial=False) == "Email is not valid."


def test_validate_user_payload_blank_password():
    payload = {
        "username": "asmaa",
        "email": "asmaa@example.com",
        "password": "",
        "role": "student",
    }
    assert validate_user_payload(payload, partial=False) == "Password is required."


def test_validate_user_payload_weak_password():
    payload = {
        "username": "asmaa",
        "email": "asmaa@example.com",
        "password": "weak",
        "role": "student",
    }
    assert (
        validate_user_payload(payload, partial=False)
        == "Password must be at least 8 characters long and include both letters and numbers."
    )


def test_validate_user_payload_invalid_role():
    payload = {
        "username": "asmaa",
        "email": "asmaa@example.com",
        "password": "Password123",
        "role": "manager",
    }
    assert (
        validate_user_payload(payload, partial=False)
        == "Role must be one of: admin, instructor, student."
    )


def test_validate_user_payload_partial_valid():
    payload = {
        "email": "updated@example.com",
        "role": "instructor",
    }
    assert validate_user_payload(payload, partial=True) is None


def test_validate_user_payload_partial_weak_password():
    payload = {"password": "weak"}
    assert (
        validate_user_payload(payload, partial=True)
        == "Password must be at least 8 characters long and include both letters and numbers."
    )
