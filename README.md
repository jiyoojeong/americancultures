# americancultures

This project scrapes university public data regarding future courses and Academic Senate approval statuses of instructors teaching ‘American Cultures’ requirement courses, a university-wide requirement that over 40,000 students have to take. Instructors must go through an application and approval process for each course to be declared as meeting this requirement. 

This software consists of several main parts:

- courses.py, senate_data.py: obtains the current information of courses being offered and the most recent senate approved data via Chrome webdriver, cleans the data, and saves the data via google cloud (pygsheets) upload for center-wide user access.
- access_sheets.py: takes the cleaned data from above to download sheets as reformatted .csv files. This data can be found in the data folder.
- sort.py: utilizes python and sqlite to create a database for all .csv data. Cross references every course instructor to the approved senate lists and creates a database for approved and not senate-approved instructors. This data is further split up to add columns based on First, Middle and Last names for ease of creating mail-merges to notify faculty and written to the google cloud.
    - looking to create a fuzzy matching between the course data and senate approved lists.


Find the finalized spreadsheet [AC Classes List](https://docs.google.com/spreadsheets/d/1hop5bnRhSSfG0EK7A8X1D5y1tmvegWcTp_m5w8esDz8/edit?usp=sharing)

SETUP:
- <code>pip install -r requirements.txt</code>
- Running the courses code:
    1. move to the directory the code files are in via terminal
    2. get new (most current term's) url: <code>python3 new_url.py</code>
    3. copy paste this new_url into the variable <code>main_url</code> on line 52 of courses.py.
    4. run scraping for classes.berkeley.edu: <code>python3 courses.py</code> 