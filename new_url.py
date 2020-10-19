import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import catahelper
import pygsheets
import csv
import time

# set up webdriver
def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("chromedriver85", options=options)

    driver.get("https://classes.berkeley.edu/search/class/")

    #ac_button = driver.find_element_by_css_selector("#facetapi-link--8775")
    ac_button = driver.find_element_by_css_selector("#facetapi-link--8786")
    ac_button.click()

    #print("ac button clicked")

    time.sleep(15)

    term_button = driver.find_element_by_xpath("//*[@id='term_0']")

    term_button.click()
    #print("term button clicked")

    ok_button = driver.find_element_by_css_selector("body > div.alertify.ajs-pulse > div.ajs-modal > div > div.ajs-footer > div.ajs-primary.ajs-buttons > button.ajs-button.ajs-cancel")
    ok_button.click()
    time.sleep(20)

    url = driver.current_url
    print(url)

    driver.quit()
    return url