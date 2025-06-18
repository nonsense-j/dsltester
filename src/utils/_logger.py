import logging
import sys
from pathlib import Path

log_level = logging.INFO

# logger Creation
logger = logging.getLogger("DSLTesterLogger")
logger.setLevel(log_level)


# console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)

# formatter
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(funcName)s - [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def set_log_file(log_file_path) -> None:
    """
    Set the log file for the logger.
    :param log_file_path: The full path to the log file.
    """
    if not isinstance(log_file_path, Path):
        log_file_path = Path(log_file_path)

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    if log_file_path.exists():
        log_file_path.unlink()
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def unset_log_file() -> None:
    """
    Unset the log file for the logger.
    """
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()
