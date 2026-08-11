import logging
import sys


def setup_logging():
    """
    Configures standard application logging.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("tenyguard")
    logger.info("Logging configured successfully.")
    return logger


logger = setup_logging()
