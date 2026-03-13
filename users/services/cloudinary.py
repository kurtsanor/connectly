import cloudinary.uploader


def upload_avatar(avatar_file) -> str:
    """
    Uploads a user avatar image to Cloudinary and returns its hosted URL.

    Resizes and center-crops the image to a 200x200 square before storing
    it in the 'avatars' folder on Cloudinary.

    Args:
        avatar_file: The image file object to upload (e.g., from request.FILES).

    Returns:
        str: The secure HTTPS URL of the uploaded avatar image.
    """
    upload_result = cloudinary.uploader.upload(
        avatar_file,
        folder="avatars",           # Store all avatars in a dedicated Cloudinary folder.
        transformation=[
            {
                "width":  200,
                "height": 200,
                "crop":   "fill"    # Center-crop the image to fit exactly 200x200.
            }
        ]
    )
    return upload_result["secure_url"]  # Return the HTTPS URL of the uploaded image.