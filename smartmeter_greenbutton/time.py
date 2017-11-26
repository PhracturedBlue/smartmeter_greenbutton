"""Elapsed time functions"""

import time
import logging

# pylint: disable=C0103
# pylint: disable=global-statement

_timestamp = time.time()

def elapsed(msg):
    """Print elapsed time"""
    global _timestamp
    new_ts = time.time()
    logging.info("%s - Elapsed time: %.3f", msg, float(new_ts - _timestamp))
    _timestamp = new_ts

def reset_elapsed():
    """Reset elapsed time"""
    global _timestamp
    _timestamp = time.time()
