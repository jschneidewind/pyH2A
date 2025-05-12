import logging
import os
from pythonjsonlogger import json

class Log_Handler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entries = []
    
    def emit(self, record):
        log_entry = self.format(record)
        self.log_entries.append(log_entry)

    def get_log_entries(self):
        return self.log_entries

def setup_logging(log_file=None):
    """
    Configures the logging system for the entire project.
    If a log_file is provided, all existing handlers will be cleared
    and new ones (file and list handlers) are added.
    """
    if log_file:
        log_directory = os.path.dirname(log_file)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

    # Get the root logger (or a specific logger, e.g., 'pyH2A')
    logger = logging.getLogger("pyH2A")
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()


    # Prevent propagation for noisy third-party libraries
    logging.getLogger("PIL").propagate = False
    logging.getLogger("matplotlib").propagate = False

    # Create a formatter using python-json-logger
    formatter = json.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create and add the custom list handler to capture logs in memory
    list_handler = Log_Handler()
    list_handler.setFormatter(formatter)
    logger.addHandler(list_handler)

    # If a log_file is provided, add a file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger, list_handler
