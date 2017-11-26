"""Fetch greenbutton data from Portland General Electric's web-page"""

import time
import logging
from selenium import webdriver
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
    browser = webdriver.PhantomJS()
    elapsed("Startup browser")
    try:
        browser.get(URL)
        found = _login(browser, conf)
        found.click()

        link = _load_greenbutton_page(browser)

        _set_date_range(browser, start_date)
        link.click()

        link = wait_for(browser, "id", "lnkDownload")
        elapsed("Loaded Download page")
        response = _download(browser, link)
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
    # browser.implicitly_wait(10)
    elem_submit = wait_for(browser, "id", "submitButton")
    elem_user = browser.find_element_by_id("userName")
    elem_password = browser.find_element_by_id("password")
    # elem_remember = browser.find_element_by_id("rememberMeCheckBox")
    elem_user.clear()
    elem_user.send_keys(conf['username'])
    elem_password.clear()
    elem_password.send_keys(conf['password'])
    elapsed("Loaded Login page")
    elem_submit.click()
    # try:
    #     while True:
    #         waiting = browser.find_element_by_xpath("//div[@cg-busy]")
    #         logging.debug("{} : {}".format(count, waiting))
    #         count += 1
    # except:
    #     pass
    found = wait_for(browser, "id", "dailyUsageLink")
    elapsed("Loaded Account page")
    return found


def _load_greenbutton_page(browser):
    browser.switch_to_window(browser.window_handles[1])
    link = wait_for(browser, "class", "GreenButton")
    elapsed("Loaded Usage page")
    link.find_element_by_tag_name("img").click()

    browser.switch_to_window(browser.window_handles[2])
    link = wait_for(browser, "id", "btnDownloadUsage")
    elapsed("Loaded Green Button page")
    return link


def _set_date_range(browser, start_date):
    # 09/23/2017
    elem_start_date = browser.find_element_by_id("calStartDate")
    if start_date:
        browser.execute_script(
            "arguments[0].removeAttribute('readonly','readonly')",
            elem_start_date)
        logging.debug("Set date to" + start_date.strftime("%m/%d/%Y"))
        elem_start_date.clear()
        elem_start_date.send_keys(start_date.strftime("%m/%d/%Y"))
    elem_end_date = browser.find_element_by_id("calEndDate")
    logging.info("Fetching data from %s to %s",
                 elem_start_date.get_attribute("value"),
                 elem_end_date.get_attribute("value"))


def _download(browser, link):
    count = 0
    while True:
        try:
            link.click()
            break
        except ElementNotVisibleException:
            count += 1
            if count >= 60:
                raise Exception
            logging.debug("Waiting for Download")
            time.sleep(1)
    response = download(browser, link)
    return response
