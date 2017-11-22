import time
import logging
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from smartmeter_greenbutton.web import (wait_for, download)
from smartmeter_greenbutton.time import (reset_elapsed, elapsed)

url = "https://cs.portlandgeneral.com"

def fetch_data(conf, start_date):
    reset_elapsed()
    # here we'll use pseudo browser PhantomJS,
    # but browser can be replaced with browser = webdriver.FireFox(),
    # which is good for debugging.
    browser = webdriver.PhantomJS()
    elapsed("Startup browser")
    browser.get(url)
    #browser.implicitly_wait(10)
    elem_user = browser.find_element_by_id("userName")
    elem_password = browser.find_element_by_id("password")
    elem_remember = browser.find_element_by_id("rememberMeCheckBox")
    elem_submit = browser.find_element_by_id("submitButton")
    elem_user.clear()
    elem_user.send_keys(conf['username'])
    elem_password.clear()
    elem_password.send_keys(conf['password'])
    elapsed("Loaded Login page")
    elem_submit.click()

    count = 0
    #try:
    #    while True:
    #        waiting = browser.find_element_by_xpath("//div[@cg-busy]")
    #        logging.debug("{} : {}".format(count, waiting))
    #        count += 1
    #except:
    #    pass
    try:
        found = wait_for(browser, "id", "dailyUsageLink")
        elapsed("Loaded Account page")
        found.click()

        browser.switch_to_window(browser.window_handles[1])
        link = wait_for(browser, "class", "GreenButton")
        elapsed("Loaded Usage page")
        link.find_element_by_tag_name("img").click()

        browser.switch_to_window(browser.window_handles[2])
        link = wait_for(browser, "id", "btnDownloadUsage")
        elapsed("Loaded Green Button page")
        # 09/23/2017
        elem_start_date = browser.find_element_by_id("calStartDate")
        #browser.execute_script("arguments[0].removeAttribute('readonly','readonly')", start_date)
        #new_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%m/%d/%Y")
        #print(new_date)
        #start_date.clear()
        #start_date.send_keys(new_date)
        elem_end_date = browser.find_element_by_id("calEndDate")
        link.click()

        link = wait_for(browser, "id", "lnkDownload")
        elapsed("Loaded Download page")
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
        browser.quit()
        return response.content

    except Exception as e:
        with open("debug.log", "w") as fh:
            fh.write("{}".format(browser.page_source))
        browser.save_screenshot("debug.png")
        browser.quit()
        raise e

