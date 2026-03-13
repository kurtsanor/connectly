from posts.pagination import CommentPagination, PostPagination

class CommentPaginatorSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CommentPagination()
        return cls._instance

class PostPaginatorSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PostPagination()
        return cls._instance