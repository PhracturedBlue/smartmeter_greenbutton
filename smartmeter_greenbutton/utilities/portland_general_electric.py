"""Fetch greenbutton data from Portland General Electric's web-page"""

import time
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (ElementNotVisibleException,
                                        WebDriverException)
from smartmeter_greenbutton.web import (wait_for, download)
from smartmeter_greenbutton.time import (reset_elapsed, elapsed)

URL = "https://cs.portlandgeneral.com"


def fetch_data(conf, start_date, retries=2):
    """Routine to scrape web-page"""

    retries -= 1
    reset_elapsed()
    # here we'll use pseudo browser PhantomJS,
    # but browser can be replaced with browser = webdriver.FireFox(),
    # which is good for debugging.
    browser = webdriver.Firefox()
    #browser = webdriver.PhantomJS()
    elapsed("Startup browser")
    try:
        browser.get(URL)
        found = _login(browser, conf)
        found.click()

        link = _load_greenbutton_page(browser)
        link = _build_download_link(browser, start_date)
        #_set_date_range(browser, start_date)
        response = download(browser, link)

        browser.quit()
        return response.content

    except WebDriverException as excpt:
        logging.error("Failed to fetch data: Error: %s", str(excpt))
        with open("debug.log", "w") as stream:
            stream.write("{}".format(browser.page_source))
        browser.save_screenshot("debug.png")
        if retries:
            logging.warning("Retrying fetch in 10 minutes")
            time.sleep(600)
            return fetch_data(conf, start_date, retries)
        browser.quit()
        raise excpt


def _login(browser, conf):
    elem_submit = wait_for(browser, "id", "submitButton")
    elem_user = browser.find_element_by_id("userNameInput")
    elem_password = browser.find_element_by_id("passwordInput")
    # elem_remember = browser.find_element_by_id("rememberMeCheckBox")
    elem_user.clear()
    elem_user.send_keys(conf['username'])
    elem_password.clear()
    elem_password.send_keys(conf['password'])
    elapsed("Loaded Login page")
    elem_submit.click()
    found = WebDriverWait(browser, 60).until(
        EC.element_to_be_clickable((By.ID, 'myUsageLink')))
    overlay = browser.find_elements_by_class_name("ng-busy-backdrop")
    for over in overlay:
        browser.execute_script("arguments[0].style.visibility='hidden'", over)
    WebDriverWait(browser, 60).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, 'ng-busy-backdrop')))
    # found = wait_for(browser, "id", "myUsageLink")
    elapsed("Loaded Account page")
    return found


def _load_greenbutton_page(browser):
    for _i in range(5):
        if len(browser.window_handles) >= 2:
            break
        time.sleep(1)
    browser.switch_to_window(browser.window_handles[1])
    link = wait_for(browser, "class", "green-button")
    elapsed("Loaded Usage page")
    link.click()
    #link.find_element_by_tag_name("img").click()

    #browser.switch_to_window(browser.window_handles[2])
    # link = browser.find_element_by_xpath("//input[@type='submit' and @value='Export']")
    link = wait_for(browser, "class", "primary")
    elapsed("Loaded Green Button page")
    return link


def _set_date_range(browser, start_date):
    # 09/23/2017
    elem_range_radio = browser.find_element_by_id("period-date")
    elem_range = elem_range_radio.find_element_by_xpath("..").find_element_by_tag_name("label")
    elem_range.click()
    elem_xml_radio = browser.find_element_by_id("format-xml")
    elem_xml = elem_xml_radio.find_element_by_xpath("..").find_element_by_tag_name("label")
    elem_xml.click()
    elem_start_date = browser.find_element_by_id("date-picker-from")
    if start_date:
        #browser.execute_script(
        #    "arguments[0].removeAttribute('readonly','readonly')",
        #    elem_start_date)
        logging.debug("Set date to" + start_date.strftime("%m/%d/%Y"))
        elem_start_date.clear()
        elem_start_date.send_keys(start_date.strftime("%m/%d/%Y"))
    elem_end_date = browser.find_element_by_id("date-picker-to")
    logging.info("Fetching data from %s to %s",
                 elem_start_date.get_attribute("value"),
                 elem_end_date.get_attribute("value"))


def _build_download_link(browser, start_date):
    """Build download link"""
    # link = "https://pgn.opower.com/ei/app/api/usage_export/download?format=xml&startDate=2018-09-08&endDate=2018-10-08"
    #import pdb; pdb.set_trace()
    url = urlparse(browser.current_url)
    if start_date:
        start_date = start_date.strftime("%Y-%m-%d")
    else:
        elem_start_date = browser.find_element_by_id("date-picker-from")
        start_date = _convert_date(elem_start_date.get_attribute("value"))
    elem_end_date = browser.find_element_by_id("date-picker-to")
    end_date = _convert_date(elem_end_date.get_attribute("value"))
    link = "{}://{}/ei/app/api/usage_export/download?format=xml&startDate={}&endDate={}".format(
        url.scheme, url.netloc,
        start_date, end_date)
    logging.info("Downloading from: %s", link)
    return link


def _convert_date(date):
    """Convert form date into HREF date"""
    month, day, year = date.split('/')
    return year + "-" + month + "-" + day
