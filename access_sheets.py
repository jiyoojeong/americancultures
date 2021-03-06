import pandas as pd
import pygsheets
import datetime as dt
import signal
import time
import csv
import re


# ==== HELPER FUNCTIONS === $

# accesses the senate and ac classes spreadsheets on google cloud to
# get and clean the data.
def access():
    # authorization
    gc = pygsheets.authorize(service_file="client_secret.json")

    file_name_1 = "AC Classes List"
    file_name_2 = 'AC Senate Data SP 2020'


    # year access
    with open('data/current_data_sem_year.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        yr = next(reader)[0]

    print('year:' + yr)
    # courses
    f1 = gc.open(file_name_1)
    print('---classes data accessed.')

    wk = f1.worksheet_by_title(yr)

    data = wk.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
    headers = data.pop(0)
    # print(headers[3:])
    headers = [re.sub(r'\s+', '_', entry) for entry in headers]
    data = reformat_values_spaces(data)
    classes = pd.DataFrame(data, columns=headers)
    print(classes)
    # reformatting instructor names
    for h in headers[3:]:
        # print(h)
        ls = classes[h]
        # print(ls)
        i = 0
        for name in ls:
            n = name.split(' ')
            # print('name list')
            # print(n)
            if len(n) <= 1:
                # THIS IS A NO INSTRUCTOR CASE
                # add to index 1 and 2 NA values
                # print('no instrructorrrrrrr')
                n = ['NA', 'NA', 'NA']
            elif len(n) == 2:
                # add middle name as NA
                # print('add middle')
                n.insert(1, 'NA')
            elif len(n) > 3:
                # join the middle X values into one 'middle' value
                # print('combine middle')
                first = n.pop(0)
                last = n.pop()
                middle = ' '.join(n)
                n = [first, middle, last]
            instructor_name = ', '.join(n)
            # print(instructor_name)
            classes.at[i, h] = instructor_name
            i = i + 1

    print('---classes data done.')

    # senate
    f2 = gc.open(file_name_2)
    senate = {}  # list of data frames with instructors based on departments.
    i = 0
    print('---senate data accessed.')
    for _ in f2:
        wk = f2[i]
        i = i + 1
        d_rows = wk.get_all_records()
        # reformat all rows to have no spaces.
        d_rows = reformat_records_spaces(d_rows)
        title = wk.title.strip()
        senate[re.sub(r'\s+', '_', title)] = d_rows
    print('---senate data done.')
    return classes, senate


def reformat_records_spaces(l):
    new = []

    for dictionary_row in l:
        count = 0
        new_d = {}
        for key in dictionary_row:
            try:
                # print(key)
                new_key = re.sub(r'\s+', "_", key)
                # print(new_key)
            except:
                print("key error.")
            val = dictionary_row.get(key)
            if count >= 1:
                if not pd.isna(val):
                    if type(val) == str:
                        val = re.sub(r'\s+', " ", val)
                        val = val.split()
                        if len(val) == 2:
                            val.insert(1, 'NA')
                        elif len(val) <= 1:
                            val = ['NA', 'NA', 'NA']
                        elif len(val) > 3:
                            first = val.pop(0)
                            last = val.pop()
                            middle = " ".join(val)
                            val = [first, middle, last]

                        val = ', '.join(val)
                    # print("value was numeric. Not a problem.")
                    # print(new_key, str(val))
                    new_d[new_key] = val
                else:
                    new_d[new_key] = 'NA, NA, NA'
            else:
                try:
                    val = re.sub(r'\s+', '_', val)
                except:
                    val = val
                new_d[new_key] = val

            count = count + 1
        new.append(new_d)
    return new


def reformat_values_spaces(l):
    new = []
    for row in l:
        # print('row' + str(row))
        new_row = []
        for entry in row:
            # print(entry)
            if not pd.isna(entry):
                e = re.sub(r'^\s', '', entry)
                e = re.sub(r'\s+', ' ', e)
            else:
                e = "NONE"
            new_row.append(e)

        new.append(new_row)
    # print(new)
    return new


# ==== DEFINE SYNONYMS ==== #

# a dictionary of 'synonymical' vocabulary referring to campus departments and academic structures.
dept_dict = {"AFRICAM": "AFRICAN AMERICAN STUDIES",
             "AMERSTD": "AMERICAN STUDIES",
             'ARCH': "ARCHITECTURE",
             'ART': "ART PRACTICE",
             'ARTHIST': "ART HISTORY",
             'HISTART': "ART HISTORY",
             'ANTHRO': "ANTHROPOLOGY",
             'ASAMST': "ASIAN AMERICAN STUDIES",
             'UGBA': "BUSINESS ADMINISTRATION (UGBA)",
             'CHICANO': "CHICANO STUDIES",
             'CYPLAN': "CITY AND REGIONAL PLANNING",
             'COLWRIT': "COLLEGE WRITING",
             'COMPLIT': "COMPARATIVE LITERATURE",
             'DEMOG': "DEMOGRAPHY",
             'DUTCH': "DUTCH STUDIES",
             'EPS': "EARTH AND PLANETARY SCIENCE",
             'EDUC': "EDUCATION",
             'ENGIN': "ENGINEERING",
             'ENGLISH': "ENGLISH",
             'ENVECON': "ENVIRONMENTAL ECONOMICS",
             'ESPM': "ENVIRONMENTAL SCIENCE, POLIC...",
             'ETHSTD': "ETHNIC STUDIES",
             'FILM': "FILM STUDIES",
             'FRENCH': "FRENCH",
             'GEOG': "GEOGRAPHY",
             'GWS': "GENDER & WOMEN’S STUDIES (fo...",
             'LGBT': "LGBT",
             'LEGALST': "LEGAL STUDIES",
             'GPP': "GLOBAL PROVERTY AND PRACTICE",
             'HISTORY': "HISTORY",
             'HUMAN BIODYNAMICS': "HUMAN BIODYNAMICS",  # MAY NEED ADJUSTMENT
             'INFO': "INFORMATION (formerly INFORM...",
             'IAS': "INTERNATIONAL AND AREA STUDIES",
             'INTEGBI': "INTEGRATIVE BIOLOGY",
             'INTERDEPARTMENTAL STUDIES': "INTERDEPARTMENTAL STUDIES",  # MAY NEED ADJUSTMENT
             'NATAMST': "NATIVE AMERICAN STUDIES",
             'PBHLTH': "PUBLIC HEALTH",
             'POLSCI': "POLITICAL SCIENCE",
             'NUSCTX': "NUTRITIONAL SCIENCE AND TOXI...",
             'SLAVIC': "SLAVIC LANGUAGES AND LITERATURE",
             'SOCIOL': "SOCIOLOGY",
             'SOCWEL': "SOCIAL WELFARE",
             'THEATER': 'THEATER, DANCE, AND PERFORMA...',
             'TDPS': "THEATER, DANCE, AND PERFORMA...",
             'UGBA': 'BUSINESS ADMINISTRATION (UGBA)',
             'UNDERGRADUATE INTERDISCIPLINATRY STUDIES': "UNDERGRADUATE AND INTERDISCI...",
             'LS': "UNDERGRADUATE AND INTERDISCI...",
             'PUBPOL': 'PUBLIC POLICY',
             'COMLIT': 'COMPARATIVE LITERATURE'
             }

# reformat spaces
dept_dict = {k: re.sub(r'\s', '_', v) for k, v in dept_dict.items()}


# ===== MAIN ===== #
def main():
    # get data from google sheets
    print("accessing....")
    courses, senate = access()
    print("accessed!")

    time.sleep(4)
    #  for every course in course list, get the department, cross check with the dictionary of departments

    # ==== PYTHON ANALYSIS ==== #
    print(courses.columns)
    dept_names_full = courses["Department_FULL"]
    dept_names_short = courses["Department"]
    print("SENATE COLUMNS")
    print(senate.keys())
    # loop through each row, check that the instructors are on the senate list.
    for c in range(0, len(dept_names_full)):
        dept_name = dept_names_full[c]
        # ETHNIC STUDIES SPECIAL CASE: check senate department of the following dictionaries instead of the regular one.
        if dept_name == "ETHNIC_STUDIES" and dept_names_short[c] != "ETHSTD":
            best_name = dept_dict[dept_names_short[c]]
            courses.at[c, 'Department_FULL'] = best_name

        if dept_name != '':
            # print("-------course dept name: " + dept_name)

            try:
                # department name is in the dictionary of senate approved.
                senate[dept_name]
            except:
                # print("Department_FULL is not in senate dictionary.")
                # trial two: use pre-made dictionary to go to senate.
                try:
                    shortened_dept_name = dept_names_short[c]
                    best_name = dept_dict[shortened_dept_name]
                    senate[best_name]
                    # print('best' + best_name)
                    courses.at[c, 'Department_FULL'] = best_name
                    # print(courses)
                except:
                    print("this one fails. May not be an approved course.")
                    # print("both trials did not work. Department long was: " + dept_name)
                    print('dept short: ' + shortened_dept_name)
                    print('dict returned: ' + dept_dict[shortened_dept_name])
                    print("class was: " + courses['Course_Number'][c])
                    continue
        else:
            continue

    print("writing clean access data to csv file.")
    now = dt.datetime.now()
    # reformat column names to _ instead of " "
    courses.columns = [re.sub(r'\s+', '_', c) for c in courses.columns]
    # split up instructor names!!

    courses.to_csv('data/{}_{}_{}_access.csv'.format(now.year, now.month, now.day))

    senate_names = []
    for s in senate:
        # trim edge white spaces
        stitle = re.sub(r'^\s', '', s)
        stitle = re.sub(r'^\s+$', '', stitle)

        # replace spaces with underscores
        stitle = re.sub(r'\s+', '_', stitle)
        # remove all non alphanumeric/_ characters
        stitle = re.sub(r'[^_|A-Z0-9]', '', stitle)
        print(stitle)
        # cols = senate[s].keys()
        # print(cols)
        if senate[s]:
            senate_names.append(stitle)
            d = pd.DataFrame(senate[s])
            d.columns = [c.replace(' ', '_') for c in d.columns]
            d.to_csv('data/senate/{}.csv'.format(stitle))
    # WRITE csv of all the senate names.
    print(senate_names)
    with open('data/senate/_department_names.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(senate_names)
    print("process completed.")


# === TIMEOUT HANDLER === #
def handler(signum, frame):
    raise Exception("took too much time")


signal.signal(signal.SIGALRM, handler)
signal.alarm(100)


# ==== RUN MAIN ===== #
main()

