"""Utility functions for web access"""

import time
import logging

import requests
from selenium.common.exceptions import NoSuchElementException


def wait_for(browser, elemtype, query, max_count=60):
    """Wait for requested element on dymanically loading pages"""
    count = 0
    while count < max_count:
        try:
            if elemtype == "id":
                found = browser.find_element_by_id(query)
            elif elemtype == "class":
                found = browser.find_element_by_class_name(query)
            else:
                print("Unknown type: {}".format(elemtype))
                break
            return found
        except NoSuchElementException:
            logging.debug("Waiting for %s = %s (Count: %d)",
                          elemtype, query, count)
            time.sleep(1)
            count += 1
    raise TimeoutError


def download(browser, link):
    """Downlaod file into variable for requested link"""
    session = requests.Session()
    cookies = browser.get_cookies()

    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    logging.debug("Fetching: %s -> %s",
                  browser.current_url,
                  link.get_attribute("href"))
    response = session.get(link.get_attribute("href"))
    return response
