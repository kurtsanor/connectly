class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Ensure only one instance of ConfigManager exists (Singleton pattern).
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Centralized application settings for pagination, analytics, and rate limiting.
        self.settings = {
            "POST_PAGINATION_SIZE": 10,
            "COMMENT_PAGINATION_SIZE": 20,
            "ENABLE_ANALYTICS": True,
            "RATE_LIMIT": 100
        }

    def get_setting(self, key):
        # Retrieve a setting by key, returns None if not found.
        return self.settings.get(key)

    def set_setting(self, key, value):
        # Update or add a setting dynamically at runtime.
        self.settings[key] = value


# Example usage: both variables point to the same Singleton instance.
config1 = ConfigManager()
config2 = ConfigManager()
