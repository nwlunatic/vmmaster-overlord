# coding: utf-8
import logging


def get_logger(name, level=None):
    if level is None:
        from .config import config
        level = config.get("LOG_LEVEL")

    log = logging.getLogger(name)
    log.setLevel(level)
    log.addHandler(logging.StreamHandler())
    return log