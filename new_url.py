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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://classes.berkeley.edu/search/class/?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures") # all AC courses.
    time.sleep(1)
    #ac_button = driver.find_element_by_css_selector("#facetapi-link--8775")
    #ac_button = driver.find_element("css-selector", "#facetapi-link--9177")
    #xpath = '//*[@id="facetapi-link--9177"]'
    #ac_button.click()

    #print("ac button clicked")

    time.sleep(5)

    term_button = driver.find_element("xpath", '//*[@name="term_select"][@tabindex=1]')
    #'//*[@id="facetapi-link--9267"]'

    term_button.click()
    #print("term button clicked")

    ok_button = driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div[4]/div[2]/button[2]")
    #driver.find_element_by_xpath
    ok_button.click()
    time.sleep(5)

    url = driver.current_url
    print(url)

    driver.quit()
    return url


if __name__ == '__main__':
    main()