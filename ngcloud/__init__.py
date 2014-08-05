import logging

__version__ = '0.2.2'

def _create_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger
