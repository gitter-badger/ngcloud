import logging

__version__ = '0.3.4'

def _create_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger
