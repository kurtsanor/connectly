import cloudinary.uploader

def upload_avatar(file) -> str:
    result = cloudinary.uploader.upload(
        file,
        folder="avatars",
        transformation=[
            {"width": 200, "height": 200, "crop": "fill"}
        ]
    )
    return result["secure_url"]