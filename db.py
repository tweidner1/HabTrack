import sqlite3
import random
from datetime import date, datetime, timedelta


def get_db(name="main.db", directory="habit profiles"):
    """
    Initialize a sqlite3 database connection.

    param name: name of the db-file
    param directory: directory of the database
    return: newly created sqlite3 database connection
    """
    db = sqlite3.connect(directory + "\\" + name)
    create_tables(db)
    return db


def get_db_name(db):
    """
    Return the name of the database file which belongs to the database connection "db".

    param db: an initialized sqlite3 database connection
    return: name of database file
    """
    cur = db.cursor()
    cur.execute("PRAGMA database_list;")
    db_dir = cur.fetchall()[0][2]
    i = len(db_dir) - 1
    db_name = ""
    while True:
        if db_dir[i] != "\\" and i >= 0:
            db_name = db_name + db_dir[i]
            i -= 1
        else:
            break
    db_name = db_name[::-1]
    return db_name


def get_databases(directory='habit profiles'):
    """
    Return all names of the database files present in the "habit profiles" folder.

    return: names of database files
    """
    import os
    files = [f for f in os.listdir(directory)]
    databases = []
    for f in files:
        if f[(len(f) - 3):len(f)] == ".db":
            databases.append(f[0:(len(f) - 3)])
    return databases


def create_tables(db):
    """
    Create tables for a database, but only if they don't exist yet.

    param db: an initialized sqlite3 database connection
    return:
    """
    cur = db.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("""CREATE TABLE IF NOT EXISTS habit (
        task TEXT PRIMARY KEY,
        periodicity TEXT,
        creation_date TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS tracking (
        habitTask TEXT,
        week TEXT,
        date TEXT,
        time TEXT,
        FOREIGN KEY (habitTask) REFERENCES habit(task) ON DELETE CASCADE)""")
    db.commit()


def add_habit(db, task, periodicity, creation_date):
    """
    Add a new habit to a database.

    param db: an initialized sqlite3 database connection
    param task: habit task
    param periodicity: habit periodicity
    param creation_date: habit creation date
    return:
    """
    cur = db.cursor()
    cur.execute("INSERT OR IGNORE INTO habit VALUES (?, ?, ?)", (task, periodicity, creation_date))
    db.commit()


def delete_habit(db, task):
    """
    Delete a habit from a database. The data record with given task is deleted from the "habit" table
    and all the referencing data records in the tracking table are deleted, too.

    param db: an initialized sqlite3 database connection
    param task: habit task of the habit to be deleted
    return:
    """
    cur = db.cursor()
    cur.execute("DELETE FROM habit WHERE task=?", (task,))
    db.commit()


def check_off_task(db, task, check_off_date=None, check_off_week=None, check_off_time=None):
    """
    "Check-off" a habit task. Check-off week, date and time is either NOW or the ones given
    as attributes if check_off_date is not None.

    param db: an initialized sqlite3 database connection
    param task: habit task to be checked-off
    param check_off_date: date of check-off
    param check_off_week: week of check-off
    param check_off_time: time of check-off
    return:
    """
    cur = db.cursor()
    if check_off_date is None:
        check_off_date = str(date.today())
        check_off_week = date.today().isocalendar()[1]
        check_off_time = datetime.now().strftime("%H:%M:%S")
    cur.execute("INSERT INTO tracking VALUES (?, ?, ?, ?)",
                (task, check_off_week, check_off_date, check_off_time))
    db.commit()


def check_off_task_today(db, task):
    """
    Check-off habit task if the task has not been checked off in the current period (day or week,
    depending on the periodicity of the given habit task).

    param db: an initialized sqlite3 database connection
    param task: habit task to be checked-off
    return:
    """
    tracking_data = get_tracking_data(db, task)
    if not tracking_data:
        check_off_task(db, task)
        if get_periodicity(db, task) == "daily":
            print(f"\"{task}\" has been checked-off for today. Good job!")
        else:
            print(f"\"{task}\" has been checked-off for this week. Good job!")
    else:
        if get_periodicity(db, task) == "daily":
            if tracking_data[len(tracking_data) - 1][2] == str(date.today()):
                print("You already checked-off this task today.")
            else:
                check_off_task(db, task)
                print(f"\"{task}\" has been checked-off for today. Good job!")
        elif get_periodicity(db, task) == "weekly":
            # check if week number AND year of last tracking entry equals the ones of today
            if (tracking_data[len(tracking_data) - 1][1] == str(date.today().isocalendar()[1]))\
                    and (tracking_data[len(tracking_data) - 1][2][0:4] == str(date.today())[0:4]):
                print("You already checked-off this task for this week.")
            else:
                check_off_task(db, task)
                print(f"\"{task}\" has been checked-off for this week. Good job!")


def get_creation_date(db, task):
    """
    Return the creation date of the given habit, represented by its task.

    param db: an initialized sqlite3 database connection
    param task: habit task
    return: creation date of given habit
    """
    cur = db.cursor()
    cur.execute("SELECT creation_date FROM habit WHERE task=?", (task,))
    return cur.fetchall()[0][0]


def get_periodicity(db, task):
    """
    Return the periodicity of the given habit, represented by its task.

    param db: an initialized sqlite3 database connection
    param task: habit task
    return: periodicity of given habit
    """
    cur = db.cursor()
    cur.execute("SELECT periodicity FROM habit WHERE task=?", (task,))
    return cur.fetchall()[0][0]


def get_habit_tasks(db):
    cur = db.cursor()
    habit_tasks = cur.execute("SELECT task FROM habit")
    tasks = []
    for x in habit_tasks:
        tasks.append(x[0])
    return tasks


def get_tracking_data(db, task=None):
    """
    Return tracking data of a database, either all the data or only the one belonging to the given habit,
    represented by its task.

    param db: an initialized sqlite3 database connection
    param task: habit task
    return: tracking data
    """
    cur = db.cursor()
    if task is None:
        cur.execute("SELECT * FROM tracking")
    else:
        cur.execute("SELECT * FROM tracking WHERE habitTask=?", (task,))
    return cur.fetchall()


def create_example_profile(name="example.db", chance_of_checkoff=75):
    """
    Create example habit tracking data.

    param name: name of the .db-file
    param chance_of_checkoff: Probability of "check-offs" during the creation of the randomized tracking data
    return:
    """

    ex_db = get_db(name)

    add_habit(ex_db, "Reading a book every day for 30min", "daily", "2022-09-02")
    add_habit(ex_db, "Not using the phone in the morning", "daily", "2022-09-04")
    add_habit(ex_db, "Completing one Duolingo French session every day", "daily", "2022-09-06")
    add_habit(ex_db, "Going into nature once a week", "weekly", "2022-09-06")
    add_habit(ex_db, "Going to the gym two times a week", "weekly", "2022-09-08")

    habit_tasks = get_habit_tasks(ex_db)
    number_of_tracking_days = 28
    number_of_tracking_weeks = 4

    # In the following, randomized tracking data will be created for the example profile. Randomizing the tracking data
    # has a few advantages:
    # 1. It makes the example tracking data look more realistic.
    # 2. It can be used to test if the analytics functionality of the app works as expected not only for one but
    # for all possible sets of tracking data.
    for x in habit_tasks:
        starting_date = date.fromisoformat(get_creation_date(ex_db, x))
        if get_periodicity(ex_db, x) == "daily":
            number_of_periods = number_of_tracking_days
        else:
            number_of_periods = number_of_tracking_weeks
        for y in range(number_of_periods):
            random_number = random.randint(1, 100)
            if random_number <= chance_of_checkoff:
                if get_periodicity(ex_db, x) == "daily":
                    new_date = starting_date + (y*timedelta(1))
                    new_week = new_date.isocalendar()[1]
                else:
                    new_week_date = starting_date + y * timedelta(7)
                    while new_week_date.weekday() > 0:
                        new_week_date = new_week_date - timedelta(1)
                    first_weekday = new_week_date
                    random_weekday_number = random.randint(0, 6)
                    new_date = first_weekday + random_weekday_number * timedelta(1)
                    new_week = new_date.isocalendar()[1]
                    if y == 0:
                        new_date = starting_date
                        new_week = starting_date.isocalendar()[1]

                # randomize the time
                random_hour = random.randint(8, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                random_datetime = datetime(1991, 3, 12, hour=random_hour,
                                           minute=random_minute, second=random_second)
                new_time = random_datetime.strftime("%H:%M:%S")

                check_off_task(ex_db, x, new_date, new_week, new_time)

    ex_db.close()
