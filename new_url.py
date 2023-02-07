import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# update chromedriver automagically
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import catahelper2 as catahelper
import pygsheets
import csv
import time

# set up webdriver
def main():
    
    # set up webdriver
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    #driver = webdriver.Chrome("/Users/jiyoojeong/Desktop/C/americancultures/chromedriver109", options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.get("https://classes.berkeley.edu/search/class/")
    time.sleep(1)
    #ac_button = driver.find_element_by_css_selector("#facetapi-link--8775")
    ac_button = driver.find_element_by_css_selector("#facetapi-link--9177")
    #xpath = '//*[@id="facetapi-link--9177"]'
    ac_button.click()

    #print("ac button clicked")

    time.sleep(5)

    term_button = driver.find_element_by_xpath('//*[@id="term_29"]')
    '//*[@id="facetapi-link--9267"]'

    term_button.click()
    #print("term button clicked")

    ok_button = driver.find_element_by_css_selector("body > div.alertify.ajs-pulse > div.ajs-modal > div > div.ajs-footer > div.ajs-primary.ajs-buttons > button.ajs-button.ajs-cancel")
    ok_button.click()
    time.sleep(5)

    url = driver.current_url
    print(url)

    driver.quit()
    return url


if __name__ == '__main__':
    main()