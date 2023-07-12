import new_url
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from installs import import_or_install as iori
import lxml

import catahelper2 as catahelper
iori('pygsheets')
import pygsheets
iori('csv')
import csv


# update chromedriver automagically
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# authorization
gc = pygsheets.authorize(service_file="client_secret.json")


# set up webdriver
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
#options.add_argument('--headless')

#driver = webdriver.Chrome("/Users/jiyoojeong/Desktop/C/americancultures/chromedriver109", options=options)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# main_url = "https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A1174&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures"
# main_url = "https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A1961&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures"
# main_url = "https://classes.berkeley.edu/search/class/?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures&f%5B1%5D=im_field_term_name%3A2176"
# main_url = new_url.main()
# 1/27 past courses list
#main_url = "https://classes.berkeley.edu/search/class/?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures&f%5B1%5D=im_field_term_name%3A2176" # SUMMER 2021
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2208&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # FALL 2021
#main_url = "https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2010&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures" # SPRING 2021
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A1961&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # Fall 2020
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A851&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # FALL 2019
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures&f%5B1%5D=im_field_term_name%3A2010' # SPRING 2021
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A865&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # SPRING 2020
#main_url = 'https://classes.berkeley.edu/search/class?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures&f%5B1%5D=im_field_term_name%3A2176&retain-filters=1' # SUMMER 2021
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2556&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # SUMMER 2022
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=sm_general_requirement%3AAmerican%20Cultures&f%5B1%5D=im_field_term_name%3A2538' # SPRING 2022
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2587&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # FALL 2022
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2729&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' #SPRING 2023
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2801&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' #SUMMER 23
main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2870&f%5B1%5D=sm_general_requirement%3AAmerican%20Cultures' # FALL 23
#main_url = '' # INSERT URL HERE.
#main_url = 'https://classes.berkeley.edu/search/class/?f%5B0%5D=im_field_term_name%3A2801&f%5B1%5D=ts_course_level%3Aup&f%5B2%5D=ts_course_level%3Alow' # all summer 23 courses, not just AC.
driver.get(main_url)
urls = {'1': main_url} 

page_number = 2

while True:
    try:
        link = driver.find_element("link text", str(page_number))
    except NoSuchElementException:
        break
    link.click()
    urls[str(page_number)] = str(driver.current_url)
    page_number += 1

# print(urls)  # prints all urls from search results

courses_split = []
instructor_list = []
depts = []
instruction_mode = []
enrollment_dat = []
course_links = []

soup = BeautifulSoup(driver.page_source, "lxml")
yr = soup.find("div", "ls-term-year")
yr = yr.get_text()
yr = yr #+ "_ALL"
print("TERM:", yr)
yrs = []

# open the sheet
file = gc.open('AC Classes List') # GOOGLE LINK HERE: https://docs.google.com/spreadsheets/d/1hop5bnRhSSfG0EK7A8X1D5y1tmvegWcTp_m5w8esDz8/edit#gid=1639877394 
sheet = file[0]  # selects the first sheet


# create a new sheet for every semester
def write_new_sheet(year):
    # col 1 dept, col 2 course num, col 3-n all instructors

    data_dict = {"Department": [i[0] for i in courses_split], "Course Number": [i[1] for i in courses_split],
                 "Instructors": instructor_list, "instruction_mode": instruction_mode}
    
    enrollment_df = pd.DataFrame(enrollment_dat)
    # print("dept:" + " len = " + str(len(data_dict["Department"])) + " " + str(data_dict["Department"]))
    # print("numb:" + " len = " + str(len(data_dict["Course Number"])) + " " + str(data_dict["Course Number"]))
    # print("inst:" + " len = " + str(len(data_dict["Instructors"])) + " " + str(data_dict["Instructors"]))
    df = pd.DataFrame(data_dict)
    df2 = df.Instructors.apply(pd.Series)  # separates instructors

    df2.insert(0, "Course Number", data_dict['Course Number'])
    df2.insert(0, "Department", data_dict['Department'])
    
    df2 = pd.concat([df2, enrollment_df], axis=1)
    #print(df2)  # check


# create a new sheet for every year
def write_sheet(year):
    # col 1 dept, col 2 course num, col 3-n all instructors

    data_dict = {"Department": [i[0] for i in courses_split], "Course Number": [i[1] for i in courses_split],
                 "Instructors": instructor_list, "Department Full": depts, "Instruction Mode": instruction_mode, "Classes Link": course_links}
    #print(len(data_dict["Department"]))
    #print(len(data_dict["Course Number"]))
    #print(len(data_dict["Instructors"]))
    print(len(data_dict["Department Full"]))
    print(len(data_dict["Instruction Mode"]))
    #print("dept:" + " len = " + str(len(data_dict["Department"])) + " " + str(data_dict["Department"]))
    #print("numb:" + " len = " + str(len(data_dict["Course Number"])) + " " + str(data_dict["Course Number"]))
    #print("inst:" + " len = " + str(len(data_dict["Instructors"])) + " " + str(data_dict["Instructors"]))
    df = pd.DataFrame(data_dict)
    df2 = df.Instructors.apply(pd.Series)  # separates instructors
    lis = []
    for c in df2.columns:
        lis.append("Instructor " + str(c + 1))
    df2.columns = lis
    df2.insert(0, "Course Number", data_dict['Course Number'])
    df2.insert(0, "Department", data_dict['Department'])
    df2.insert(1, "Department_FULL", data_dict['Department Full'])
    df2.insert(2, "Instruction Mode", data_dict['Instruction Mode'])
    df2.insert(3, "Classes Links", data_dict["Classes Link"])

    enrollment_df = pd.DataFrame(enrollment_dat)
    df2 = pd.concat([df2, enrollment_df], axis=1)

    #print(df2)  # check
    return df2


# use cata-helper to go through each page
for page in urls:
    print("running page " + page)

    helper_course, helper_instructors, helper_yr, helper_depts, helper_instruction_mode, helper_enrollment, helper_links = catahelper.main(urls[page], driver)

    courses_split.extend(helper_course)
    instructor_list.extend(helper_instructors)
    depts.extend(helper_depts)
    instruction_mode.extend(helper_instruction_mode)
    enrollment_dat.extend(helper_enrollment)
    course_links.extend(helper_links)
    try:
        yr = helper_yr[:19]
    except:
        yr = helper_yr
        
    #print(courses_split)
    #print(instructor_list)

# update sheet on google drive

with open('data/current_data_sem_year.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow([yr])
print("process completed.")

try: 
    sheet = file.add_worksheet(yr)
    sheet.set_dataframe(write_sheet(yr), (1, 1))
except:
    print('sheet exists.')
    sheet = file.worksheet_by_title(yr)
    sheet.clear()
    sheet.set_dataframe(write_sheet(yr), (1, 1))
    print('URL OF SHEET:', sheet.url)
    #print(sheet)

driver.quit()