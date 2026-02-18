# posts/pagination.py
from rest_framework.pagination import PageNumberPagination
from connectly.singletons.config_manager import ConfigManager

config = ConfigManager()

class PostPagination(PageNumberPagination):
    page_size = config.get_setting('DEFAULT_PAGE_SIZE')

class CommentPagination(PageNumberPagination):
    page_size = config.get_setting('DEFAULT_PAGE_SIZE')