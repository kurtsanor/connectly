from rest_framework.pagination import PageNumberPagination
from connectly.singletons.config_manager import ConfigManager

# Retrieve shared configuration settings via Singleton.
config = ConfigManager()

class PostPagination(PageNumberPagination):
    """
    Pagination class for Post objects.
    Uses the configured page size from ConfigManager to ensure consistency.
    """
    # Default number of posts per page, pulled from config.
    page_size = config.get_setting('POST_PAGINATION_SIZE')
    page_size_query_param = 'page_size'  # allow clients to override
    # max number of posts per page, pulled from config.
    max_page_size = config.get_setting('POST_MAX_PAGE_SIZE')

class CommentPagination(PageNumberPagination):
    """
    Pagination class for Comment objects.
    Uses the configured page size from ConfigManager to ensure consistency.
    """
    # Default number of comments per page, pulled from config.
    page_size = config.get_setting('COMMENT_PAGINATION_SIZE')
