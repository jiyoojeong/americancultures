import googleapiclient
import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
import pygsheets
import time as time
import signal
import re
import lxml.html
import lxml.html.clean


# === TIMEOUT HANDLER === #
def handler(signum, frame):
    print(1)
    raise Exception("took too much time")


signal.signal(signal.SIGALRM, handler)
signal.alarm(45)


# ==== SIDE FUNCTIONS ==== #

# takes in a @param 'url' string url to the senate data page.
# It will set up google authorization and the webdriver to scrape data.
def collect_url(url):
    # authorization
    gc = pygsheets.authorize(service_file="client_secret.json")
    res = requests.get(url)

    # print(res)
    if res.status_code == 200:
        print("server answered http request. proceeding...")
    return gc, res


# takes in @ param 'res' url request to scrape the desired data from the site.
# In this case, it will click all drop down boxes to get all the approved instructors.
# this data is poorly formatted on the website and requires lots of cleaning.
def scrape(res):
    # === formatting === #


    soup = BeautifulSoup(res.content, "lxml")




    # all department names
    dept_list = soup.findAll("h2", {"class": "openberkeley-collapsible-controller"})
    dept_stripped = []  # this is the header for all the departments
    for t in dept_list:
        # print("----testing----")
        # print(t.get_text())
        # print("----end----")
        dept_name = t.get_text()
        if len(dept_name) > 31:
            dept_name = dept_name[0:28] + "..."
        dept_stripped.append(dept_name)

    # remove empty categorical variables to ensure correct data matching
    dept_stripped.remove("DRAMATIC ART—see Theater, Da...")
    dept_stripped.remove("LIBRARY AND INFORMATION STUD...")
    # print(dept_stripped)  # prints out all departments in list

    # drop content
    drop_content = soup.findAll("div", {"class": "openberkeley-collapsible-target"})

    return drop_content, dept_stripped


# takes in @param content (which is the scraped items in the list, drop-content
# gets the text and removes all special characters.
#
def clean(d):
    s = d.get_text()
    # print("original s: " + s)

    # remove all parenthetical notes.
    s = re.sub(r'\(.+\)', '', s)
    # remove &nbsp; chars.
    s = re.sub(r'\u00A0', ' ', s)
    # substitute all bullets as 'NEXT' for easily identifying instructor passage.
    s = re.sub(r'[•]', 'NEXT', s)
    # use regex to remove all non-alpha numeric numbers and replace them with the empty string.
    s = re.sub(r'[^\s a-zA-Z0-9áéèíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ]', '', s)
    # whitespace reformatting
    s = re.sub(' +', ' ', s)

    print("regex clean done" + s)

    col = []
    profs = []

    # loop through the string in departments
    while "\n" in s:
        # pops off first approved course list off of department as s1
        s1 = s[0:s.index("\n")]  # everything before the enter
        the_rest = s[s.index("\n") + 1:]  # everything after the enter
        # print("----s1----")
        # print(s1)
        # print("----s2----")
        # print(the_rest)
        s = the_rest
        if s1:
            profs = profs + [separate(s1, col)]  # all the profs approved for one course
    return np.c_[col, profs]  # return the column binded values of col and prof


# separate takes in @param 'bits' which consists of a string of all instructors.
# @param 'c' is an empty array that gets filled with atomized versions of every instructor's name.
def separate(bits, c):
    # make an array of professors approved
    p = []
    try:
        course_no = bits[0:bits.index(" ")]
        # print("bit1 " + bit1)
        bits = bits[len(bits) - len(bits.lstrip()):]
    except:
        # case where only the name is in the senate list, no notes or instructors
        c.append(bits)
        p.append("NA")
        return p  # end function

    try:
        bit3 = bits[bits.index(" ") + 1:]
        # print("bit3 " + bit3)
        while bit3:
            try:
                p.append(bit3[0: bit3.index("NEXT")].strip())
                bit3 = bit3[bit3.index("NEXT") + 4:]
            except:  # only one prof
                p.append(bit3.strip())
                bit3 = ""
        # print("--p")
        # print(p)
    except:
        bit3 = "NA"
        p.append(bit3)

    #  add class to c (col)
    c.append(course_no)
    return p


# Writes in the @param 'df' dataframe of cleaned pandas data into the google sheet.
def write_new_file(filename, gc, depts):
    # open the sheet
    file = gc.open(filename)
    sheet_index = 0

    # for every department, create a data spreadsheet
    for dept in depts:
        if sheet_index == 0:
            print("first")
            print(dept)
            sheet = file[sheet_index]  # selects the first sheet
            sheet.title = dept  # renames just the first sheet, because the rest are done automatically.
        else:
            print(dept)
            try:
                sheet = file.add_worksheet(dept)
            except googleapiclient.errors.HttpError:
                sheet = file[sheet_index]

        matrix = depts[dept]
        instructors = matrix[:, 1]
        data_dict = {'Class': matrix[:, 0], 'instructors': instructors}

        df = pd.DataFrame(data_dict)
        df2 = df.instructors.apply(pd.Series)  # separates instructors
        lis = []
        for c in df2.columns:
            lis.append("Instructor " + str(c + 1))
        df2.columns = lis
        df = pd.DataFrame({'Class': data_dict['Class']})
        df2.insert(0, "Course Number", data_dict['Class'])

        try:
            sheet.set_dataframe(df2, (1, 1))
            for i in range(1, 2):
                time.sleep(1)
        except:
            print("timeout error.")

        sheet_index = sheet_index + 1

        # print(df2)


# ===== MAIN ===== #
# This class acquires, cleans and writes clean data onto files on google drive.


def main():
    # =========== MAIN VARIABLES ========== #
    url = "https://academic-senate.berkeley.edu/committees/amcult/approved-berkeley"
    # dictionary, key of department titles, value of matrix with course numbers and a list of all instructors
    depts = {}

    # ====== SETUP ===== #
    gc, res = collect_url(url)

    # === SCRAPE ==== #
    # use Beautiful Soup to get the javascript embedded data on the website.
    drop_content, dept_stripped = scrape(res)

    # ==== CLEAN ==== #
    print("begin restructure of drop content")

    for d in drop_content:
        plist = clean(d)
        # print(plist)
        depts[dept_stripped.pop(0)] = plist

    print("finished reformatting. writing!")

    # ==== WRITE ==== #
    filename = 'AC Senate Data SP 2020'
    try:
        write_new_file(filename, gc, depts)
    except:
        print("file already exists. update " + filename + " instead.")


# ==== RUN MAIN ==== #
main()
