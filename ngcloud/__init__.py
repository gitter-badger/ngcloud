import logging

__version__ = '0.0.4'

_log_formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(name)-20s][%(funcName)s] %(message)s')

def _create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())
    return logger
