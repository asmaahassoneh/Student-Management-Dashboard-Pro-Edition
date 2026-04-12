import cloudinary.uploader
from flask import current_app, has_app_context
from werkzeug.utils import secure_filename

from app.services.service_exceptions import ValidationError


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_profile_picture(file, upload_folder=None, allowed_extensions=None):
    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)

    if not allowed_file(filename, allowed_extensions or set()):
        return None

    if has_app_context() and current_app.config.get("TESTING"):
        return f"/fake/path/{filename}"

    try:
        result = cloudinary.uploader.upload(
            file,
            folder="student_dashboard/profile_pictures",
            resource_type="image",
        )
        return result["secure_url"]
    except Exception as exc:
        print("Cloudinary upload error:", exc)
        raise ValidationError("Failed to upload profile picture.") from exc
