import requests
import time
import logging

def wait_for(browser, elemtype, query, max_count = 60):
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
        except:
            logging.debug("Waiting for {} = {} (Count: {})".format(elemtype, query, count))
            time.sleep(1)
            count += 1
    raise Exception

def download(browser, link):
    session = requests.Session()
    cookies = browser.get_cookies()

    for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
    logging.debug("Fetching: {} -> {}".format(browser.current_url, link.get_attribute("href")))
    response = session.get(link.get_attribute("href"))
    return response

