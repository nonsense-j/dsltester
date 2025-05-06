import logging
import sys

log_level = logging.INFO

# logger Creation
logger = logging.getLogger("DSLTesterLogger")
logger.setLevel(log_level)

# handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)

# formatter
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(funcName)s - [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)

logger.addHandler(handler)
