import sqlite3
import pandas as pd
import datetime
import re
import pygsheets
import googleapiclient
import csv

# ==== Import Clean Courses Data ==== #
now = datetime.datetime.now()
path = 'data/{}_{}_{}_access.csv'.format(now.year, now.month, now.day)
df = pd.read_csv(path, index_col=0)
print(df)
# data readjustment for this package:
dept_names_full = df["Department_FULL"]
for dep in range(0, len(dept_names_full)):
    dept_name = dept_names_full[dep]
    # print(dept_name)
    dt = re.sub(r'\s', '_', dept_name)
    t = re.sub(r'[^_|A-Z0-9]', '', dt)
    # print(t)
    df.at[dep, 'Department_FULL'] = t
    # print('-------')
# print(df['Department_FULL'])


# ==== CONNECTION SETUP ==== #
def engine():
    # engine
    conn = sqlite3.connect('data/analysis.db')
    conn.text_factory = str
    print("opened database successfully!")
    return conn


# ==== SETUP SENATE TABLE ==== #

# update_senate()
senate_folder = 'data/senate'


def setup_all_senate(con, folder_path):
    p = "{}/{}".format(folder_path, '_department_names.csv')
    depts = pd.read_csv(p)

    for d in depts:
        p = "{}/{}.csv".format(folder_path, d)
        # print(re.sub(r'\s', '_', d))
        title = re.sub(r'\s', '_', d)
        title = re.sub(r'[^_|A-Z0-9]', '', title)
        dept_block = pd.read_csv(p, index_col=0)
        print(title)
        print(dept_block)
        try:
            dept_block.to_sql(title, con, if_exists='replace', index=False)
        except:
            print('no data frame.')
        # clear old temp tables
        cur.execute('''DROP TABLE IF EXISTS {d}_fl'''.format(d=d))
        cur.execute('''DROP TABLE IF EXISTS A_{d}'''.format(d=d))


# ==== SETUP CLASSES TABLE==== #
def setup_table(con, df):
    df.to_sql('courses', con, if_exists='replace', index=False)

# ==== CLOUD METHODS ==== #


def client_auth():
    # authorization
    gc = pygsheets.authorize(service_file="client_secret.json")
    return gc


# takes in a list of sql database table names. Writes these onto a cloud.
def write_to_cloud(ls, filename, con):
    gc = client_auth()
    file = gc.open(filename)
    dict = {'whole': 'Approved',
            'not_approved': 'Not Approved'
            }
    with open('data/current_data_sem_year.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        sem = next(reader)

    for add_ons in ls:
        df = pd.read_sql_query('''SELECT * FROM {}'''.format(add_ons), con)
        df = beautify(df)
        try:
            sheet = file.add_worksheet(dict[add_ons]+'{}'.format(sem))
        except googleapiclient.errors.HttpError:
            sheet = file.worksheet_by_title(dict[add_ons]+'{}'.format(sem))
            sheet.clear()
        sheet.set_dataframe(df, (1, 1))


def beautify(df):
    ind = 3
    for instr in range(0, len(course_columns_limited)):
        first = []
        middle = []
        last = []
        name_ls = df[course_columns_limited[instr]]
        for name_ind in range(0, len(name_ls)):
            name = name_ls[name_ind]
            try:
                name = re.sub(r'_+', ' ', name)
                name = re.sub(r'\.', '', name)
                split = name.split(', ')
                if len(split) == 2:
                    split.insert(1, ' ')
                # print(split)
                first.append(split[0])
                middle.append(split[1])
                last.append(split[2])
            except:
                # print('n= ' + str(name))
                first.append(name)
                middle.append(name)
                last.append(name)
        df.insert(ind, "Inst_{}_First".format(instr + 1), first, True)
        ind = ind + 1
        df.insert(ind, "Inst_{}_Middle".format(instr + 1), middle, True)
        ind = ind + 1
        df.insert(ind, "Inst_{}_Last".format(instr + 1), last, True)
        ind = ind + 1

        ind = ind + 1
    return df


# === CREATE SQL TABLES === #
connection = engine()
cur = connection.cursor()
setup_all_senate(connection, senate_folder)
setup_table(connection, df)

print("All SQL tables created. Begin analysis.")

# === MAIN ANALYSIS === #

     #===== RESET DB ==== #

cur.execute('''DROP TABLE IF EXISTS not_approved''')
cur.execute('''DROP TABLE IF EXISTS whole''')

course_depts = cur.execute(
    '''SELECT name FROM sqlite_master WHERE type='table';''')
senate_0 = [tuple[0] for tuple in course_depts][0]
# print(senate_0)

# == get senate column names == #
cur.execute('''SELECT * FROM {}'''.format(senate_0))
# print(senate_columns)
cur.execute('''CREATE TABLE IF NOT EXISTS not_approved AS 
                SELECT * FROM courses''')

cur.execute('''SELECT * FROM courses''')

course_columns = [description[0] for description in cur.description]

# == FORMAT column name lists == #
course_columns_limited = course_columns.copy()
try:
    course_columns_limited.remove("Course_Number")
    course_columns_limited.remove("Department_FULL")
    course_columns_limited.remove("Department")
except:
    print("do nothing")


# return to all
current_table = cur.execute(
    '''SELECT name FROM sqlite_master WHERE type='table';''')
current_table = [d for d in current_table]

for dept in current_table:
    if dept[0] == "courses" or dept[0] == "not_approved":
        continue

    print('******current senate table: ' + dept[0])

    # === SETTING UP SENATE COLUMNS - each department is different === #
    cur.execute('''SELECT * FROM {}'''.format(dept[0]))
    senate_columns = [description[0] for description in cur.description]
    senate_columns_limited = senate_columns.copy()
    try:
        senate_columns_limited.remove("Course_Number")
    except:
        print("nothing")

    senate_collapsed = ', '.join(senate_columns_limited)
    senate_call = ['senate.' + x for x in senate_columns_limited]
    senate_call_cat = ' || -- || '.join(senate_call)
    # print(senate_call_cat)

    # === CREATE APPROVAL TABLES === #
    # create one table for all approved ac courses and instructors.
    # courses that have the same dept and course number as approved list
    query = ''' 
    CREATE TEMPORARY TABLE TEMP_{d} AS
    SELECT c.*
    FROM courses AS c, {d} AS d
    WHERE (c.Course_Number = d.Course_Number
    AND c.Department_FULL = "{d}")
    '''.format(d=dept[0])

    c = cur.execute(query)
    c = cur.execute('''SELECT * FROM TEMP_{d}'''.format(d=dept[0]))
    # assert len(c.fetchall()) == 0, "TEMP_{d} isnt empty...\n{f}".format(d=dept[0], f=c.fetchall())

    # selects first and last names as separate columns of instructors in course matches
    cur.execute('''
                CREATE TABLE {d}_fl(
                    name TEXT);
            '''.format(d=dept[0]))

    # loop through the current table to further filter by approved instructor.
    for inst in course_columns_limited:
        # select only if the inst column of courses is like any of the senates
        # print(inst)

        # First and Last entries of column inst, separated by delimiter '_'
        # fill this query out based on adjusted course data access.
        query = '''
            INSERT INTO {d}_fl(name)
            SELECT t.{i}
            FROM TEMP_{d} as t
        '''.format(d=dept[0], i=inst)
        cur.execute(query)

        # print out list of first and last of instructors teaching dept/courses on senate list
        # print(cur.execute('''select * from {d}_fl'''.format(d=dept[0])).fetchall())

        # Check first and last are on approved senate list!
        # ? is a concatenated version of each Instructor Name from the senate tables.
        # LIKE compares it to the recent classes names from the table temp_{d}
        # we also want to filter out the No-Instructor Values,
        #   by comparing u.name (the name of the current column instructor) does not have 'NA', 'NA', 'NA'
        cur.execute('''DROP TABLE IF EXISTS A_{}'''.format(dept[0]))

        query = '''
            CREATE TABLE A_{d} AS
            SELECT c.*
            FROM TEMP_{d} AS c
            LEFT OUTER JOIN
                    ((SELECT {s} FROM {d} AS senate)
                    INNER JOIN {d}_fl AS name) AS u
                ON ? LIKE u.name OR ? LIKE u.name
        '''.format(d=dept[0], s=senate_collapsed)


        THeres something wrong with not comparing the second instructor. Need to adjust so that
        the query loop from inst in course columns limited also checks the second instructor when Not 'nanana' and
        removes those not approved from the approved list

        this should be done by comparing if its instructor_1 or not
        if not instructor one, we do the same comparison but we remove from A_{} rather than adding to it at the end.
        cur.execute(query, (senate_call_cat, senate_call_cat))

        fetch = cur.execute(
            '''SELECT Instructor_1 FROM A_{d} WHERE Instructor_1 = 'NA, NA, NA' '''.format(d=dept[0])).fetchall()

        if fetch:
            print("~~~~~this is it~~~~~")
            print('deleting...')
            print("== BEFORE ==")
            f = cur.execute('''SELECT * from A_{d}'''.format(d=dept[0])).fetchall()
            print(f)

            query = '''
                        DELETE FROM A_{d} 
                        WHERE Instructor_1 = 'NA, NA, NA'
                    '''.format(d=dept[0])

            cur.execute(query)
            print('== AFTER ==')
            f = cur.execute('''SELECT * from A_{d}'''.format(d=dept[0])).fetchall()
            print(f)

        else:
            print('')

        fetch = cur.execute('''SELECT * from A_{d}'''.format(d=dept[0])).fetchall()
        if fetch:
            print('approved for this department:')
            print(fetch)
        else:
            continue


        # TEMP_{d} is a table with only approved instructors
        cur.execute('''SELECT * FROM TEMP_{d} INNER JOIN A_{d};'''.format(d=dept[0]))
        # print(cur.execute('''SELECT * FROM TEMP_{}'''.format(dept[0])).fetchall())
        cur.execute('''DROP TABLE IF EXISTS temp''')
        cur.execute('''DROP TABLE IF EXISTS A_{}'''.format(dept[0]))

        # print('np and temp')
        # print(cur.execute('''select * from not_approved''').fetchall())
        # print(cur.execute('''select * from TEMP_{d}'''.format(d=dept[0])).fetchall())

        # === SEPARATE APPROVED AND NON APPROVED COURSES === #
        cur.execute('''DELETE FROM not_approved
                    WHERE EXISTS (SELECT t.*
                                  FROM TEMP_{d} t
                                  WHERE (t.Course_Number = not_approved.Course_Number 
                                  AND t.Department = not_approved.Department)
                                  )'''.format(d=dept[0]))
        # print('post deleting.')
        # print(cur.execute('''select * from not_approved''').fetchall())
    cur.execute('''DROP TABLE IF EXISTS TEMP_{d}'''.format(d=dept[0]))
    cur.execute('''DROP TABLE IF EXISTS {}_fl'''.format(dept[0]))
    print('****** MOVE SENATE TABLE')
    # print(senate_call_cat)


# === WHOLE table represents approved courses === #

cur.execute('''CREATE TABLE whole AS
                SELECT c.*
                FROM courses AS c
                LEFT JOIN not_approved AS nap
                ON (c.Course_Number == nap.Course_Number
                    AND c.Department_FULL == nap.Department_FULL)
                WHERE nap.Course_Number IS NULL
                ;''')

print("CHECK FIN")
cur.execute('''SELECT * FROM courses''')
print(len(cur.fetchall()))
print(cur.execute('''SELECT * FROM courses''').fetchall())

cur.execute('''SELECT * FROM whole''')
print(len(cur.fetchall()))
print(cur.execute('''SELECT * FROM whole''').fetchall())

cur.execute('''SELECT * FROM not_approved''')
print(len(cur.fetchall()))
print(cur.execute('''SELECT * FROM not_approved''').fetchall())

write_to_cloud(['whole', 'not_approved'], 'AC Classes List', connection)
connection.close()
