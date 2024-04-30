import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)s %(name)s %(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_logger():
    return logging.getLogger(__name__)


# The code snippet above shows the logger initialization in the __init__.py file.
