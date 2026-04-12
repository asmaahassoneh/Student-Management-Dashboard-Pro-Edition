import os
import cloudinary


def configure_cloudinary():
    cloudinary_url = os.getenv("CLOUDINARY_URL")

    if not cloudinary_url:
        raise RuntimeError("CLOUDINARY_URL is not set.")

    cloudinary.config(
        cloudinary_url=cloudinary_url,
        secure=True,
    )
