import pygsheets
import gspread
import difflib
import re


# Google Sheets
client_auth()
# Open the google spreadsheet (by its name)
sheet = client.open('AC Classes List').sheet1

# Get all the names in the spreadsheet
names = [item[i] for item in sheet.get_all_values()]
departments = [item[j] for item in sheet.get_all_values()]
course_num = [item[k] for item in sheet.get_all_values()]


def client_auth():
    # authorization
    # using pygsheets
    if use_pyg:
        gc = pygsheets.authorize(service_file="client_secret.json")
        return gc
    # using gspread
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    return client

    


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


# Now check if the names are in the Google Spreadsheet
for name, course in names:
    closest_match = difflib.get_close_matches(name, spreadsheet_values, n=1, cutoff=0.6)
    if closest_match:
        print(f'{name} who teaches {course} is probably in the spreadsheet as {closest_match[0]}.')
    else:
        print(f'{name} who teaches {course} is not in the spreadsheet.')






# pseudocode
