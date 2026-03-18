from posts.pagination import CommentPagination, PostPagination

class CommentPaginatorSingleton:
    """
    Singleton wrapper for CommentPagination.
    Ensures only one shared paginator instance is used across all views.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        # Return the existing instance if it exists,
        # otherwise create a new CommentPagination instance.
        if cls._instance is None:
            cls._instance = CommentPagination()
        return cls._instance


class PostPaginatorSingleton:
    """
    Singleton wrapper for PostPagination.
    Provides a single reusable paginator instance for all post-related views.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        # Return the existing instance if it exists,
        # otherwise create a new PostPagination instance.
        if cls._instance is None:
            cls._instance = PostPagination()
        return cls._instance
