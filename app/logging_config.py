# Sistema de logging ainda em desenvolvimento...

import logging
from logging.handlers import RotatingFileHandler
import os

# Diretório dos logs
LOG_DIR = "/root/netmore-api/logs"
os.makedirs(LOG_DIR, exist_ok=True)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

def setup_logger(name, log_file, level=logging.INFO):
    """Configura e retorna um logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Loggers específicos
important_changes_logger = setup_logger(
    "important_changes", os.path.join(LOG_DIR, "important_changes.log")
)
error_logger = setup_logger(
    "error_logger", os.path.join(LOG_DIR, "errors.log")
)
security_logger = setup_logger(
    "security_logger", os.path.join(LOG_DIR, "security.log")
)
access_logger = setup_logger(
    "access_logger", os.path.join(LOG_DIR, "access.log")
)
fetch_data_logger = setup_logger(
    "fetch_data_logger", os.path.join(LOG_DIR, "fetch_data.log")
)
process_images_logger = setup_logger(
    "process_images_logger", os.path.join(LOG_DIR, "process_images.log")
)
