import time
import logging

ts = time.time()

def elapsed(s):
    global ts
    new_ts = time.time()
    logging.info("{} - Elapsed time: {}".format(s, new_ts - ts))
    ts = new_ts

def reset_elapsed():
    global ts
    ts = time.time()

