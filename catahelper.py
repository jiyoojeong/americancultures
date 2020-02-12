import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver


# takes in url, outputs arrays courses[dept, course number], instructors[], and string year-semester
def main(url):
    # setting up webscraping driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("/Users/jiyoojeong/Downloads/chromedriver", options=options)

    driver.get(url)
    test_a = driver.find_element_by_class_name("ls-instructors")

    # Beautiful Souping - finding components on page, stripping jQuery, java, html, etc.
    soup = BeautifulSoup(driver.page_source, "lxml")

    # year
    yr = soup.find("div", "ls-term-year")
    yr = yr.get_text()
    # print(yr)

    # instructors

    names_list = soup.findAll("div", "ls-instructors")
    instructor_list = []
    for t in names_list:
        # print("-----new t------")
        r = t.findAll("span")
        inst = []
        for x in r:
            x = x.get_text()
            if not x == '':
                # print(x)
                inst.append(x)
        instructor_list.append(inst)
    # instructor_list = [list(t) for t in set(tuple(element) for element in instructor_list)]

    # organizing courses from a page
    classes_list = soup.findAll("span", "ls-section-name")

    dept_list = soup.findAll("span", "ls-section-dept")

    # dept_list = soup.findAll("a", target="_blank")
    section = soup.findAll("span", "ls-section-count")
    # print("len section" + str(len(section)))
    # print(section)
    # print("len classes" + str(len(classes_list)))

    classes_list = []
    dept_list = []
    section = []
    names_list = []

    # === TRYING NEW CODE === #
    search_res = soup.findAll('div', 'col-wrapper')
    for sr in search_res:
        classes_list.append(sr.find("span", "ls-section-name"))
        dept_list.append(sr.find("span", "ls-section-dept"))
        section.append(sr.find("span", "ls-section-count"))
        names_list.append(sr.findAll("div",  "ls-instructors"))

    # print(names_list)
    instructor_list = []
    for t in names_list:
        # print("-----new t------")
        # print(t)
        if not t:
            instructor_list.append(["NA"])
        else:
            for r in t:
                b = r.get_text()
                try:
                    ls = b.replace('\n', '')
                    ls = ls.split(',')
                except:
                    ls = [b.replace('\n', '')]
                instructor_list.append(ls)
    # print("~~~~~~~~~~ INSTRUCTOR LIST ~~~~~~~~")
    # print(instructor_list)
    # print(section)

    courses = []
    for c in classes_list:
        c = c.get_text()
        c.strip()
        courses.append([c, section.pop(0).get_text()])

    dept_stripped = []
    # creating dictionary of departments
    for d in dept_list:
        d = d.get_text()
        d.strip()
        # print(d)
        d = d[16:]
        d = d.upper()
        dept_stripped.append(d)
        # print(d)
        # print("new")

    # filtering through duplicates
    i = 0
    while i < len(courses) - 1:
        name1 = courses[i][0]
        name2 = courses[i+1][0]
        name1.replace("\\s", "")
        name2.replace("\\s", "")

        if name1 == name2 and courses[i][1] == courses[i+1][1]:
            courses.pop(i)
            dept_stripped.pop(i)
            # duplicates within html file - example: two section 001s
        elif name1 == name2 and instructor_list[i] == instructor_list[i+1]:
            # print("dupe")
            courses.pop(i)
            dept_stripped.pop(i)
            instructor_list.pop(i)
            # duplicate course sections 001, 002, etc.
        else:
            i += 1

    # cases for no instructor
    tot = list(range(len(courses) - 1))
    for i in tot:
        if courses[i][0] == courses[i+1][0] and len(instructor_list) < len(courses):
            # duplicate course sections, no instructor recorded.
            print("NO INST")
            # print(courses)
            # print(instructor_list)
            courses.pop(i)
            dept_stripped.pop(i)
            i -= 1
            tot.pop(-1)
        if len(instructor_list) < len(courses):
            instructor_list.insert(i, "NA")

    courses = [i[0] for i in courses]

    # testing section by printing

    print('Courses     ' + str(courses))
    print('Instructors ' + str(instructor_list))

    # restructuring courses
    courses_split = []
    for c in courses:
        # print("---c begins---")
        # print(c)
        # print("---c ends----")
        courses_split.append(c.split())

    print("courses split" + str(courses_split))

    return courses_split, instructor_list, yr, dept_stripped
