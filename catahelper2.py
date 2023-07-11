from installs import import_or_install as iori

from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
import numpy as np

find_instr_mode = True
import time
# update chromedriver automagically

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# waits
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# takes in url, outputs arrays courses[dept, course number], instructors[], and string year-semester
def main(url, driver=None):
    # setting up webscraping driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    #driver = webdriver.Chrome("/Users/jiyoojeong/Desktop/C/americancultures/chromedriver109", options=options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if driver==None:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    #test_a = driver.find_element_by_class_name("ls-instructors")

    # Beautiful Souping - finding components on page, stripping jQuery, java, html, etc.
    soup = BeautifulSoup(driver.page_source, "lxml")

    # year
    yr = soup.find("div", "ls-term-year")
    yr = yr.get_text()
    # print(yr)

    # instructors
    try:
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
    except Exception:
        print("no instructors on this page.")
        instructor_list = []

    # organizing courses from a page
    classes_list = soup.findAll("span", "ls-section-name")

    dept_list = soup.findAll("span", "ls-section-dept")

    # dept_list = soup.findAll("a", target="_blank")
    section = soup.findAll("span", "ls-section-count")
    # print("len section" + str(len(section)))
    # print(section)
    # print("len classes" + str(len(classes_list)))
    instmode = soup.findAll('span', 'ls-instructor-mode')

    #print(instmode)
    #print('TEST... past instmode')

    classes_list = []
    dept_list = []
    section = []
    names_list = []
    links = []
    instruction_mode = []

    # === TRYING NEW CODE === #
    search_res = soup.findAll('div', 'col-wrapper')
    for sr in search_res:
        #iprint(sr)
        classes_list.append(sr.find("span", "ls-section-name"))
        dept_list.append(sr.find("span", "ls-section-dept"))
        section.append(sr.find("span", "ls-section-count"))
        names_list.append(sr.findAll("div",  "ls-instructors"))
        links.append(sr.findAll("a", "ls-section-wrapper"))
        # Instruction mode for COVID procedures 
        try:
            #print('1')
            im = sr.find('div', 'ls-instructor-mode-flex fspmedium')
            #'/html/body/div[1]/div[2]/main/div/div/ol/li[11]/div/div/div[1]/div[1]/div[1]/div[5]/p/span[2]'
            #print('2')
            spans = im.findAll('span')
            #print([s.text for s in spans])
            #print('3')
            #spans=[im.text]
        except:
            spans = []
            #print(spans)
        if find_instr_mode and len(spans) == 2:
            #print('spans', spans, 'len', len(spans))
            instruction_mode.append(spans[1].text)
        else:
            instruction_mode.append('NA')
    #print(len(classes_list), len(dept_list), len(section), len(instruction_mode))
    #print(names_list)
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
    #print("~~~~~~~~~~ INSTRUCTOR LIST ~~~~~~~~")
    #print(instructor_list)
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
        
        
    # extract link from a tag for links
    hrefs = []
    for wrapper in links:
       #print(wrapper[0])
        l = wrapper[0]
        if l.has_attr('href'):
            hrefs.append(l['href'])
        else:
            hrefs.append("NA")
    #print(hrefs)

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
            instruction_mode.pop(i)
            hrefs.pop(i)
            #pass # DO NOTHING. We don't want to remove duplicates.
            # duplicates within html file - example: two section 001s
        #elif name1 == name2 and instructor_list[i] == instructor_list[i+1]:
            # print("dupe")
            #courses.pop(i)
            #dept_stripped.pop(i)
            #instructor_list.pop(i)
            #instruction_mode.pop(i)
            #pass # DO NOTHING. We do want duplicate course sections.
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
            instruction_mode.pop(i)
            hrefs.pop(i)
            i -= 1
            tot.pop(-1)

        if len(instructor_list) < len(courses):
            instructor_list.insert(i, "NA")


    courses = [i[0] for i in courses]

    # testing section by printing

    #print(len(courses)) #, 'Courses     ' + str(courses))
    #print(len(instructor_list))#, 'Instructors ' + str(instructor_list))
    #print(len(instruction_mode))#, "Instruction Mode " + str(instruction_mode))

    # restructuring courses
    courses_split = []
    for c in courses:
        # print("---c begins---")
        # print(c)
        # print("---c ends----")
        courses_split.append(c.split())

    #print("courses split" + str(courses_split))
    
    
    # ACCESS HREF course specific page
    rt = 'https://classes.berkeley.edu/'
    enrollment_dat = []
    course_links = []
    for path in hrefs:
        # go to rt + path page
        #print(rt+path)
        driver.get(rt+path)
        course_links.append(rt + path)
        try:
            #cel = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div')))
            #                                                                               '/html/body/div[2]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div'
            time.sleep(2)
            #test = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div')
            #print(test.text)
            celement = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div')))
            #print(celement.text)
            seat_info = process_class_enrollment(celement)
            #print('worked1')
        except TimeoutException:
            try:
                celement = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/main/div/div/div[1]/div/div[3]/section[1]/div')))
                seat_info = process_class_enrollment(celement)
             
            except TimeoutException:
                try:
                    test = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div')
                    seat_info = process_class_enrollment(test)
                    #print('worked3')
                except:
                    try:
                        test = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/div/div/div[1]/div/div[3]/section[1]/div')
                        seat_info = process_class_enrollment(test)
                        #print('worked4')
                    except:
                        seat_info = {"Total Open Seats": None, "Enrolled": None, "Waitlisted": None,
                         "Capacity": None, "Waitlist Max": None, "Open Reserved Seats": None}
    
        #print(seat_info)
        enrollment_dat.append(seat_info)
        #print('ce', course_enrollment)
        #print(course_enrollment)
        #break
        

    return courses_split, instructor_list, yr, dept_stripped, instruction_mode, enrollment_dat, course_links




def process_class_enrollment(elem):
    course_enrollment = elem.text #driver.find_element_by_xpath('/html/body/div[1]/div[2]/main/div/div/div[1]/div/div[2]/section[1]/div').get_text #soup.find("div", "section-details")
    course_enrollment_list = course_enrollment.split('\n')
    print(course_enrollment_list)
    if "Consent of instructor required for enrollment." in course_enrollment_list:
        course_enrollment_list.remove("Consent of instructor required for enrollment.")
        #print('removed consent line.')
    if "Consent of department required for enrollment." in course_enrollment_list:
        course_enrollment_list.remove("Consent of department required for enrollment.")
        #print('removed consent line.')
    if "No Reserved Seats" in course_enrollment_list:
        i = course_enrollment_list.index("No Reserved Seats")
        course_enrollment_list[i] = "Open Reserved Seats: None Reserved"
    elif "Open Reserved Seats:" in course_enrollment_list:
        i = course_enrollment_list.index("Open Reserved Seats:")
        course_enrollment_list[i] = "Open Reserved Seats:"
        for j in range(i+1, len(course_enrollment_list)):
            dept_seat = course_enrollment_list[j]
            if 'reserved' in dept_seat:
                dept_seat = dept_seat.replace(":", ' ')
                course_enrollment_list[i] += dept_seat + ", "
        course_enrollment_list = course_enrollment_list[0:i+1]
    
    seat_info = dict((a.strip(), b.strip())  
                for a, b in (element.split(':')  
                    for element in course_enrollment_list))  
    
    return seat_info