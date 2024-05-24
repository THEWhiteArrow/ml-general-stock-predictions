import sys
import logging


def setup_logger(name: str | None = None):
    logging.basicConfig(
        level=logging.WARNING,
        stream=sys.stdout,
        format="%(levelname)s %(name)s %(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    logger = logging.getLogger(name or __name__)
    logger.setLevel(logging.INFO)

    return logger
