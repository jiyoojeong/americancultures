import courses
import new_url
import senate_data
import schedule
import time


def main():
    # run downloads
    print("I'm working...")
    new_url.main()
    print("finished 1")
    courses.main()
    senate_data.main()
    print("finished updating.")


schedule.every().day.at("6:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
    # send email
