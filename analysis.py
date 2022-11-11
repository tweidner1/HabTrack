from db import get_db, get_databases, get_habit_tasks, get_tracking_data, get_creation_date, get_periodicity
from datetime import date, timedelta


def print_currently_tracked_habits(db, periodicity=None):
    """
    Print the currently tracked habit tasks together with their respective periodicity and creation date.
    periodicity = None -> all habit tasks are printed
    periodicity = "daily" -> only daily habit tasks are printed
    periodicity = "weekly" -> only weekly habit tasks are printed

    param db: an initialized sqlite3 database connection
    param periodicity: periodicity of the habit task
    return:
    """
    habit_tasks = get_habit_tasks(db)
    i = 1

    if periodicity is None:
        print("Your currently tracked habits:")
        for x in habit_tasks:
            print(str(i) + ". " + x + " (" + get_periodicity(db, x) +
                  ", since " + get_creation_date(db, x) + ")")
            i += 1

    elif periodicity == "daily":
        print("Your currently tracked daily habits:")
        for x in habit_tasks:
            if get_periodicity(db, x) == "daily":
                print(str(i) + ". " + x + " (" + get_periodicity(db, x) +
                      ", since " + get_creation_date(db, x) + ")")
                i += 1

    elif periodicity == "weekly":
        print("Your currently tracked weekly habits:")
        for x in habit_tasks:
            if get_periodicity(db, x) == "weekly":
                print(str(i) + ". " + x + " (" + get_periodicity(db, x) +
                      ", since " + get_creation_date(db, x) + ")")
                i += 1


def get_last_and_longest_streak(db, task):
    """
    Calculate the last and longest run streak for the given habit, represented by its task.

    param db: an initialized sqlite3 database connection
    param task: habit task
    return: last and longest run streak for given habit
    """

    def get_first_weekday_object(date_object):
        """
        Returns the first day of a specific week of the year as a date object, where the week
        is extracted from the given date object.

        param date_object: date object that holds the week of interest
        return: date object of the first day of a specific week of the year
        """
        while date_object.weekday() > 0:
            date_object = date_object - timedelta(1)
        return date_object

    tracking_data = get_tracking_data(db, task)
    streak_counter = 1
    highest_count_yet = 0

    if not tracking_data:
        streak_counter = 0
    else:
        starting_date = date.fromisoformat(tracking_data[0][2])
        for idx, x in enumerate(tracking_data):
            if get_periodicity(db, task) == "daily":
                check_off_date = date.fromisoformat(x[2])
                time_delta = 1
                if idx == 0:
                    starting_date = date.fromisoformat(tracking_data[0][2])
            else:
                check_off_date = get_first_weekday_object(date.fromisoformat(x[2]))
                time_delta = 7
                if idx == 0:
                    starting_date = get_first_weekday_object(date.fromisoformat(tracking_data[0][2]))
            if (check_off_date - timedelta(time_delta)) == starting_date:
                streak_counter += 1
                starting_date = check_off_date
            else:
                if streak_counter > highest_count_yet:
                    highest_count_yet = streak_counter
                starting_date = check_off_date
                streak_counter = 1

    # when leaving the loop, streak_counter carries the last run streak
    last_streak = streak_counter

    if streak_counter > highest_count_yet:
        highest_count_yet = streak_counter

    return last_streak, highest_count_yet


def get_overall_longest_streak(db):
    """
    Calculate the longest run streak over all habits stored in a given database.

    param db: an initialized sqlite3 database connection
    return: longest run streak over all habits together with the respective habit(s) holding that streak
    """

    habits_streaks = {}
    habits_with_longest_streaks = []
    habit_tasks = get_habit_tasks(db)
    if not habit_tasks:
        overall_longest_streak = 0
        habits_with_longest_streaks = []
    else:
        for x in habit_tasks:
            longest_streak = get_last_and_longest_streak(db, x)[1]
            habits_streaks.update({x: longest_streak})
        overall_longest_streak = max(habits_streaks.values())
        for x in habits_streaks:
            if habits_streaks.get(x) == overall_longest_streak:
                habits_with_longest_streaks.append(x)

    return overall_longest_streak, habits_with_longest_streaks


def get_overall_longest_streak_all_databases(directory="habit profiles"):
    """
    Calculate the longest run streak over all habits and all databases.

    param directory: directory with the databases of interest
    return: longest run streak over all habits and all profiles together with the respective habit(s) holding
    that streak
    """

    db_files = get_databases(directory)
    streak_data = []
    streaks = []
    for x in db_files:
        db_file = x + ".db"
        next_db = get_db(db_file, directory)
        overall_longest_streak = list(get_overall_longest_streak(next_db))
        streaks.append(overall_longest_streak[0])
        overall_longest_streak.append(x)
        streak_data.append(overall_longest_streak)
        next_db.close()

    longest_streak = max(streaks)
    longest_streak_habits_dbs = []
    for x in streak_data:
        if x[0] == longest_streak:
            longest_streak_habits_dbs.append(x[1:3])

    # longest_streak_habits_dbs example:
    # [[["habit1", "habit2"], "database1.db"], [["habit3"], "database3.db"]]
    return longest_streak, longest_streak_habits_dbs
