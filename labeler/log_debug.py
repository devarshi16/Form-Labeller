from time import ctime, time

from .config import ALLOWED_DEBUG_LEVEL, DEBUGGING, LOG_FILE, LOGGING


def logger(in_log):
    if LOGGING:
        curr_time = ctime(time())
        with open(LOG_FILE, "a") as f:
            f.write(curr_time + " " + in_log + "\n")


def debug(level, in_debug):
    if DEBUGGING:
        if level >= ALLOWED_DEBUG_LEVEL:
            print("DEBUG: " + in_debug + "\n")
