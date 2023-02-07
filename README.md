# americancultures

This project scrapes university public data regarding future courses and Academic Senate approval statuses of instructors teaching ‘American Cultures’ requirement courses, a university-wide requirement that over 30,000 students have to take. Instructors must go through an application and approval process for each course to be declared as meeting this requirement. 

This software consists of several main parts:

- course-data-multiple.py, senate_data.py: obtains the current information of courses being offered and the most recent senate approved data via Chrome webdriver, cleans the data, and saves the data via google cloud (pygsheets) upload for center-wide user access.
- access_sheets.py: takes the cleaned data from above to download sheets as reformatted .csv files. This data can be found in the data folder.
- sort.py: utilizes python and sqlite to create a database for all .csv data. Cross references every course instructor to the approved senate lists and creates a database for approved and not senate-approved instructors. This data is further split up to add columns based on First, Middle and Last names for ease of creating mail-merges to notify faculty and written to the google cloud.


Find the finalized spreadsheet [here](https://docs.google.com/spreadsheets/d/1hop5bnRhSSfG0EK7A8X1D5y1tmvegWcTp_m5w8esDz8/edit?usp=sharing)

SETUP:
- <code>pip install -r requirements.txt</code>