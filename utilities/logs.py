import logging
import os
from datetime import datetime

# Logging globals
LOGGING_DIR = None
LOG_LEVEL = None

LOG_FORMATTER = logging.Formatter("%(asctime)s  %(levelname)s  %(message)s")

# setup_logging
# creates and manages time-stamped directory where all log files are written
# should only be called once
def setup_logging(log_level):
    global LOGGING_DIR
    global LOG_LEVEL

    cur_datetime = datetime.now().strftime("%m%d%Y_%H%M%S")
    LOGGING_DIR = "logs_%s" % cur_datetime
    LOG_LEVEL = log_level

    os.mkdir(LOGGING_DIR)

# create_log
# Creates a new log file with the given name. Returns logging object that will log to this file
def create_log(log_name):
    # Throw exception if setup_logging not already called
    if(LOGGING_DIR is None):
        raise ValueError("setup_logging not called prior to trying to use create_log")

    full_log_path = os.path.join(LOGGING_DIR, "%s.log" % log_name)

    handler = logging.FileHandler(full_log_path)
    handler.setFormatter(LOG_FORMATTER)

    logger = logging.getLogger(log_name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    return logger
