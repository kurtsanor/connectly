from ..models import Post

class PostFactory:
    """
    Factory class for creating Post objects.
    Centralizes validation and construction logic for different post types.
    """

    @staticmethod
    def create_post(post_type, title, author, privacy, content='', metadata=None):
        """
        Creates a new Post instance with validation rules applied.
        """

        # Validate that the post_type is one of the allowed types.
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError(f"Invalid post type. Valid types are {Post.POST_TYPES}")

        # Ensure metadata is always a dictionary, even if None is passed.
        safe_metadata = metadata or {}

        # Enforce type-specific metadata requirements.
        if post_type == 'image' and 'file_size' not in safe_metadata:
            raise ValueError("Image posts require 'file_size' in metadata")

        if post_type == 'video' and 'duration' not in safe_metadata:
            raise ValueError("Video posts require 'duration' in metadata")

        # Validate privacy type.
        if privacy not in dict(Post.PRIVACY_TYPES):
            raise ValueError(f"Invalid privacy. Valid types are {Post.PRIVACY_TYPES}")

        # Create and return the Post instance.
        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author,
            privacy=privacy
        )
