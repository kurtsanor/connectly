import logging

class LoggerSingleton:
    """
    Singleton wrapper for Python's logging.Logger.
    Ensures that only one logger instance is created and reused across the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Return the existing instance if it exists,
        # otherwise create a new LoggerSingleton and initialize it.
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Configure the logger with a stream handler and formatter.
        self.logger = logging.getLogger("connectly_logger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        # Return the shared logger instance.
        return self.logger
