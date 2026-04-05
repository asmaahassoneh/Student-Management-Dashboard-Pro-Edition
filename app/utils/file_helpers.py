import os
import uuid
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_profile_picture(file_storage, upload_folder, allowed_extensions):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename, allowed_extensions):
        return None

    os.makedirs(upload_folder, exist_ok=True)

    extension = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename.rsplit('.', 1)[0]}.{extension}"
    save_path = os.path.join(upload_folder, unique_name)
    file_storage.save(save_path)

    return unique_name
