from habit import Habit, DBHabit
from db import get_tracking_data, get_db, add_habit, delete_habit, check_off_task, get_db_name, \
    get_databases, get_creation_date, get_periodicity, get_habit_tasks
from analysis import get_overall_longest_streak_all_databases, \
    get_last_and_longest_streak, get_overall_longest_streak
from datetime import date


class TestHabit:

    def setup_method(self):
        # set up a first database "test.db" manually
        self.db = get_db("profiles for testing\\test.db")
        add_habit(self.db, "Gardening for 30min every day", "daily", "2022-09-05")
        add_habit(self.db, "Practice Calisthenics in a park once a week", "weekly", "2022-09-07")
        add_habit(self.db, "dummy habit", "daily", "2022-09-07")
        delete_habit(self.db, "dummy habit")
        check_off_task(self.db, "Gardening for 30min every day", "2022-09-06", "36", "14:45:03")
        check_off_task(self.db, "Gardening for 30min every day", "2022-09-07", "36", "13:49:34")
        check_off_task(self.db, "Gardening for 30min every day", "2022-09-08", "36", "20:13:58")
        check_off_task(self.db, "Gardening for 30min every day", "2022-09-10", "36", "15:11:38")
        check_off_task(self.db, "Practice Calisthenics in a park once a week", "2022-09-07", "36", "08:13:51")
        check_off_task(self.db, "Practice Calisthenics in a park once a week", "2022-09-20", "38", "21:15:38")
        check_off_task(self.db, "Practice Calisthenics in a park once a week", "2022-09-29", "49", "13:16:54")

        # A second database "example.db" was created by the create_example_profile()
        # function from the "db" module. It will be tested in "test_example_data".
        # A copy of "example.db" is kept in the "habit profiles"-folder for usage
        # in HabTrack, e.g. to play around with the analytics functions.

    def test_db(self):
        db_name = get_db_name(self.db)
        assert db_name == "test.db"
        databases = get_databases("habit profiles\\profiles for testing")
        assert len(databases) == 2

    def test_habit(self):
        habit = Habit("Going for a 30min walk every day", "daily")
        print(habit.task)
        print(habit.periodicity)
        print(habit.creation_date)

    def test_db_habit(self):
        creation_date = get_creation_date(self.db, "Gardening for 30min every day")
        assert creation_date == "2022-09-05"
        periodicity = get_periodicity(self.db, "Practice Calisthenics in a park once a week")
        assert periodicity == "weekly"
        habit_data = get_habit_tasks(self.db)
        assert len(habit_data) == 2
        tracking_data = get_tracking_data(self.db, "Gardening for 30min every day")
        assert len(tracking_data) == 4

        habit_tasks = get_habit_tasks(self.db)
        assert len(habit_tasks) == 2
        streak = get_last_and_longest_streak(self.db, "Gardening for 30min every day")
        assert streak[0] == 1  # last streak
        assert streak[1] == 3  # longest streak
        overall_streak = get_overall_longest_streak(self.db)
        assert overall_streak[0] == 3
        assert overall_streak[1][0] == "Gardening for 30min every day"

        test_habit = DBHabit("Going for a 30min walk every day", "daily")
        print(test_habit.task)
        print(test_habit.periodicity)
        print(test_habit.creation_date)
        test_habit.store(self.db)

        habit_data = get_habit_tasks(self.db)
        assert len(habit_data) == 3
        test_habit.check_off(self.db)
        tracking_data = get_tracking_data(self.db, "Going for a 30min walk every day")
        assert tracking_data[0][2] == str(date.today())

        test_habit_2 = DBHabit("dummy habit", "weekly")
        test_habit_2.store(self.db)
        test_habit_2.delete(self.db)
        assert len(habit_data) == 3

    def test_example_data(self):
        self.db = get_db("profiles for testing\\example.db")
        habit_tasks = get_habit_tasks(self.db)
        for x in habit_tasks:
            streak = get_last_and_longest_streak(self.db, x)
            if x == "Reading a book every day for 30min":
                assert streak[0] == 2  # last streak
                assert streak[1] == 5  # longest streak
            elif x == "Not using the phone in the morning":
                assert streak[0] == 6
                assert streak[1] == 6
            elif x == "Completing one Duolingo French session every day":
                assert streak[0] == 8
                assert streak[1] == 8
            elif x == "Going into nature once a week":
                assert streak[0] == 1
                assert streak[1] == 1
            else:  # "Going to the gym two times a week"
                assert streak[0] == 3
                assert streak[1] == 3

        overall_streak = get_overall_longest_streak(self.db)
        assert overall_streak[0] == 8
        assert overall_streak[1][0] == "Completing one Duolingo French session every day"

        longest_streak_over_all_databases = get_overall_longest_streak_all_databases(
            directory="habit profiles\\profiles for testing")
        # example for the return of get_overall_longest_streak_over_all_databases()[1]:
        # [[["habit1", "habit2"], "database1.db"], [["habit3"], "database3.db"]]
        assert longest_streak_over_all_databases[0] == 8
        assert longest_streak_over_all_databases[1][0][0][0] == "Completing one Duolingo French session every day"
        assert longest_streak_over_all_databases[1][0][1] + ".db" == "example.db"

    def teardown_method(self):
        self.db.close()
        import os
        os.remove("habit profiles\\profiles for testing\\test.db")
        # since the database "example.db" is not altered during the testing,
        # there is no need to reset it after every testing run.
