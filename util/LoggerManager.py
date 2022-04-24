import sys
import os
import logging.handlers
from config.config import *

initializedOnce = False


def get_logger(name):

    global initializedOnce
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    file_handler = logging.handlers.RotatingFileHandler(log_file, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    should_roll = os.path.isfile(log_file)
    if initializedOnce is False and should_roll:
        file_handler.doRollover()
        initializedOnce = True

    logger.setLevel(log_level)
    return logger
