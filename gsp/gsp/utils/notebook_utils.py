from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def show(*args):
    try:
        from IPython.display import display

        for obj in args:
            display(obj)
    except ImportError:
        logger.info("IPython not found. Cannot display objects.")
