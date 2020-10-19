import courses
import new_url
import senate_data
import schedule
import time
import os


def main():
    # run downloads
    print("I'm working...")
    new_url.main()
    # print("finished 1")
    os.system('python courses.py')
    senate_data.main()
    print("finished updating.")


# schedule.every().day.at("06:00").do(main)

# while True:
     # schedule.run_pending()
     # time.sleep(1)
    # send email

if __name__ == "__main__":
    main()

