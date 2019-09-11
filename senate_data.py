import googleapiclient
import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
import pygsheets


# authorization
gc = pygsheets.authorize(service_file="/Users/jiyoojeong/Desktop/americancultures/client_secret.json")

url = "https://academic-senate.berkeley.edu/committees/amcult/approved-berkeley"
names = {"DeluganC12AC":"Delugan\nC12AC", "Rosenbaum133AC":"Rosenbaum\n133AC"}  # formatting err cases
depts = {}  # dictionary, key of department titles, value of matrix with course numbers and a list of all instructors

res = requests.get(url)
# print(res)
if res.status_code == 200:
    print("server answered http request. proceeding...")

# Beautiful Souping - finding components on page, stripping jQuery, java, html, etc.
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

# print(dept_stripped)  # prints out all departments in list

# drop content
drop_content = soup.findAll("div", {"class": "openberkeley-collapsible-target"})
drop_list_stripped = []  # list of all objects within drop content, stripped of code


# separates a line which is a class to become separate for class/instructors/notes
def separate(bits, c):
    # make an array of professors approved
    p = []
    # strip class name and () notes if any
    # print("bits " + bits)
    try:
        bit1 = bits[0:bits.index(" ")]
        # print("bit1 " + bit1)
        bits = bits[len(bits) - len(bits.lstrip()):]
    except:
        # case where only the name is in the senate list, no notes or instructors
        c.append(bits)
        p.append("NA")
        return p  # end function

    # case if there is a note appended with ( )
    try:
        bit2 = bits[bits.index("(") + 1:bits.index(")")]  # additional notes
        bits = bits[bits.index(")") + 1:]
        # print("bit2 " + bit2)
    except:
        bit2 = "none noted"

    try:
        bit3 = bits[bits.index(" ") + 1:]
        # print("bit3 " + bit3)
        while bit3:
            try:
                p.append(bit3[0: bit3.index("•")].strip())
                bit3 = bit3[bit3.index("•") + 1:]
            except:  # only one prof
                p.append(bit3.strip())
                bit3 = ""
        # print("--p")
        # print(p)
    except:
        bit3 = "NA"
        p.append(bit3)

    #  add class to c (col)
    c.append(bit1)
    return p


print("begin restructure of drop content")
dept_stripped_copy = dept_stripped
for d in drop_content:
    s = d.get_text()
    s = s.replace(u'\xa0', u' ')

    # temporary fix for names
    for n in names:
        s = s.replace(n, names[n])

    # print("----drop content----")
    # print(s)
    # print("----end drop content----")

    # drop_list_stripped.append(s)
    # print(drop_list_stripped)

    col = []
    profs = []

    while "\n" in s:
        s1 = s[0:s.index("\n")]  # everything before the enter
        s2 = s[s.index("\n") + 1:]   # everything after the enter
        # print("----s1----")
        # print(s1)
        # print("----s2----")
        # print(s2)
        s = s2
        dept_profs = []
        dept_cols = []
        if s1:
            # print("--sep--")
            profs = profs + [separate(s1, col)]  # all the profs approved for one course
            # print(col)
            # print(profs)
    master = np.c_[col, profs]
    depts[dept_stripped_copy.pop(0)] = master
    # print("master " + str(master))

# print(classes_stripped)
# print(depts)
print("finished reformatting. writing into xlsx file")

writer = pd.ExcelWriter('/Users/americancultures/Desktop/senate.xlsx', engine='xlsxwriter')

#open the sheet
file = gc.open('Senate Approved AC Instructors')
sheet_index = 0


# for every department, create a data spreadsheet
for dept in depts:
    if sheet_index == 0:
        print(dept + "first")
        sheet = file[sheet_index]  # selects the first sheet

    else:
        print(dept)
        try:
            sheet = file.add_worksheet(dept)
        except googleapiclient.errors.HttpError:
            sheet = file[sheet_index]
    sheet.title = dept
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
    df2.insert(0, "Course Number",  data_dict['Class'])

    sheet.set_dataframe(df2, (1, 1))
    sheet_index = sheet_index + 1

    # print(df2)




