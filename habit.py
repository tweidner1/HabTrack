from datetime import date
from db import check_off_task_today, add_habit, delete_habit


class Habit:

    def __init__(self, task, periodicity):
        """
        Habit class, to create habits with a certain task, periodicity and creation date.

        param task: habit task (e.g. "Not using the phone in the morning")
        param periodicity: habit periodicity can be "daily" or "weekly"
        """
        self.task = task
        self.periodicity = periodicity
        self.creation_date = date.today()


class DBHabit(Habit):

    def check_off(self, db):
        """
        Check-off the task of a habit. Adds a new entry into the "tracking" table for the given habit.

        param db: an initialized sqlite3 database connection
        return:
        """
        check_off_task_today(db, self.task)

    def store(self, db):
        """
        Store a habit in the given database.

        param db: an initialized sqlite3 database connection
        return:
        """
        add_habit(db, self.task, self.periodicity, self.creation_date)

    def delete(self, db):
        """
        Delete a habit from the given database.

        param db: an initialized sqlite3 database connection
        return:
        """
        delete_habit(db, self.task)
