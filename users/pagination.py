from rest_framework.pagination import PageNumberPagination
from connectly.singletons.config_manager import ConfigManager

config = ConfigManager()

class UserPagination(PageNumberPagination):
    """
    Pagination class for User objects.
    Uses the configured page size from ConfigManager to ensure consistency.
    """
    # Default number of comments per page, pulled from config.
    page_size = config.get_setting('USER_PAGINATION_SIZE')