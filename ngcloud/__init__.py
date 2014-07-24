import logging

__version__ = '0.0.5'

_log_formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)-7s][%(name)-8s][%(funcName)-8s] %(message)s',
    '%Y-%m-%d %H:%M:%S'
)

def _create_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger
