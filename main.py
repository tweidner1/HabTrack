import sqlite3
from habit import DBHabit
from db import get_db, get_db_name, get_databases, get_habit_tasks, get_creation_date, get_periodicity, \
    get_tracking_data, create_example_profile
from analysis import get_overall_longest_streak_all_databases, get_overall_longest_streak, \
    print_currently_tracked_habits, get_last_and_longest_streak
from prettytable import PrettyTable
import questionary
import json


def cli():
    """
    Start the habit tracking app. This will open a command line interface that can be used to navigate through the app.

    return:
    """

    with open("config.json") as outfile:
        config = json.load(outfile)
    default_db = config["default_profile"] + ".db"
    db = get_db(default_db)

    while True:

        choice = questionary.select("HabTrack", choices=["Tracker", "Profile", "EXIT"], qmark="").ask()

        if choice == "Tracker":

            while True:

                db_name = get_db_name(db)
                db_name = db_name[0: (len(db_name) - 3)]

                choice = questionary.select("Profile: " + db_name, choices=["Create new habit", "Delete habit",
                                                                            "Check-off task", "Analyze", "EXIT"],
                                            qmark="").ask()

                if choice == "Create new habit":
                    habit_tasks = get_habit_tasks(db)
                    while True:
                        task = questionary.text(("Please enter the habit task (e.g. \"Not using the phone in the "
                                                 "morning\"): ")).ask()
                        if task in habit_tasks:
                            print("The chosen habit task already exists. Try again with a different habit task.")
                        else:
                            break
                    periodicity_choice = questionary.select("Choose the periodicity for your new habit:",
                                                            choices=["daily", "weekly"]).ask()
                    new_habit = DBHabit(task, periodicity_choice)
                    new_habit.store(db)
                    print(f"The habit \"{task}\" has been created successfully. Have fun!")

                elif choice == "Delete habit":
                    habit_tasks = get_habit_tasks(db)
                    habit_tasks.append("EXIT")
                    habit_task = questionary.select("Which habit do you want to delete?",
                                                    choices=habit_tasks).ask()
                    if habit_task == "EXIT":
                        pass
                    else:
                        confirmation = questionary.confirm(
                            "Do you really want to delete the habit \"" + habit_task + "\"?").ask()
                        if confirmation:
                            new_habit = DBHabit(habit_task, "no periodicity")
                            new_habit.delete(db)
                            # upper two lines could be replaced by: delete_habit(db, habit_task)
                            print(f"The habit \"{habit_task}\" has been deleted.")
                        else:
                            pass

                elif choice == "Check-off task":
                    habit_tasks = get_habit_tasks(db)
                    habit_tasks.append("EXIT")
                    habit_task = questionary.select("Which habit task do you want to check-off?",
                                                    choices=habit_tasks).ask()
                    if habit_task == "EXIT":
                        pass
                    else:
                        new_habit = DBHabit(habit_task, "no periodicity")
                        new_habit.check_off(db)
                        # upper two lines could be replaced by: check_off_task_today(db, habit_task)
                        last_streak = get_last_and_longest_streak(db, habit_task)[0]
                        if 3 < last_streak < 10:
                            print("You are on a run streak of " + str(last_streak) + "! Good job, keep going!")
                        elif last_streak >= 10:
                            print("You are on a run streak of " + str(last_streak) + "! FANTASTIC job! Keep going!")

                elif choice == "Analyze":
                    while True:
                        analyze_choice = questionary.select("What do you want to analyze?",
                                                            choices=["Return all tracking data for a given habit",
                                                                     "Return a list of all currently tracked habits",
                                                                     ("Return a list of all habits with a specified"
                                                                      " periodicity"),
                                                                     "Return the last run streak for a given habit",
                                                                     "Return the longest run streak for a given habit",
                                                                     ("Return the longest run streak of all defined "
                                                                      "habits"),
                                                                     ("Return the longest run streak of all defined "
                                                                      "habits over ALL profiles"),
                                                                     "EXIT"], qmark="").ask()

                        if analyze_choice == "Return all tracking data for a given habit":
                            habit_tasks = get_habit_tasks(db)
                            habit_tasks.append("EXIT")
                            habit_task = questionary.select("For which habit do you want to see the habit data?",
                                                            choices=habit_tasks).ask()
                            if habit_task == "EXIT":
                                pass
                            else:
                                tracking_data = get_tracking_data(db, habit_task)
                                print("Habit: " + habit_task + " (periodicity: " + get_periodicity(db, habit_task) +
                                      ", creation date: " + get_creation_date(db, habit_task) + ")")
                                print("Tracking data: ")
                                pretty_table = PrettyTable(['Week', 'Date', 'Time'])
                                for x in tracking_data:
                                    pretty_table.add_row(x[1:4])
                                print(pretty_table)

                        elif analyze_choice == "Return a list of all currently tracked habits":
                            print_currently_tracked_habits(db, periodicity=None)

                        elif analyze_choice == "Return a list of all habits with a specified periodicity":
                            period_choice = questionary.select(("Do you want to see the habit data of "
                                                                "daily or weekly habits?"),
                                                               choices=["daily", "weekly"]).ask()
                            print_currently_tracked_habits(db, periodicity=period_choice)

                        elif analyze_choice == "Return the last run streak for a given habit":
                            habit_tasks = get_habit_tasks(db)
                            habit_tasks.append("EXIT")
                            habit_task = questionary.select(
                                "For which habit do you want to get its last run streak?",
                                choices=habit_tasks).ask()
                            last_streak = get_last_and_longest_streak(db, habit_task)[0]
                            print("The last run streak for the habit \"" + habit_task + "\" is: " + str(
                                last_streak))

                        elif analyze_choice == "Return the longest run streak for a given habit":
                            habit_tasks = get_habit_tasks(db)
                            habit_tasks.append("EXIT")
                            habit_task = questionary.select(
                                "For which habit do you want to get its longest run streak?",
                                choices=habit_tasks).ask()
                            longest_streak = get_last_and_longest_streak(db, habit_task)[1]
                            print("The longest run streak for the habit \"" + habit_task + "\" is: " + str(
                                longest_streak))

                        elif analyze_choice == "Return the longest run streak of all defined habits":
                            overall_longest_streak = get_overall_longest_streak(db)
                            print("The overall longest run streak of " + str(overall_longest_streak[0]) +
                                  " belongs to the habit(s):")
                            for x in overall_longest_streak[1]:
                                print(x)

                        elif analyze_choice == "Return the longest run streak of all defined habits over ALL profiles":
                            longest_streak = get_overall_longest_streak_all_databases()[0]
                            longest_streak_habits_dbs = get_overall_longest_streak_all_databases()[1]
                            # longest_streak_habits_dbs example:
                            # [[["habit1", "habit2"], "database1.db"], [["habit3"], "database3.db"]]
                            print("The longest run streak of all defined habits over ALL profiles is " +
                                  str(longest_streak) + " and has been achieved for the following habit(s):")
                            pretty_table = PrettyTable(['Profile', 'Habit'])
                            for x in longest_streak_habits_dbs:
                                for y in x[0]:
                                    row = [x[1], y]
                                    pretty_table.add_row(row)
                            print(pretty_table)

                        elif analyze_choice == "EXIT":
                            break

                elif choice == "EXIT":
                    break

        elif choice == "Profile":

            while True:

                profile_choice = questionary.select("What do you want to do?",
                                                    choices=["Create new profile", "Delete profile",
                                                             "Load existing profile",
                                                             "Set default profile", "Create example profile", "EXIT"],
                                                    qmark="").ask()

                if profile_choice == "Create new profile":
                    databases = get_databases()
                    while True:
                        new_db = questionary.text("Choose a name for your new habit profile: ").ask()
                        if new_db in databases:
                            print("There is already a profile with this name. Try again with a different name.")
                        else:
                            new_db_ = new_db + ".db"
                            try:
                                db = get_db(name=new_db_)
                                print(f"The profile \"{new_db}\" has been created and loaded. "
                                      f"Start your journey by creating some habits for your new profile. Good luck!")
                                break
                            except sqlite3.OperationalError:
                                print("The profile name must not contain any special characters. Please try again with "
                                      "a different profile name.")
                    break

                elif profile_choice == "Delete profile":
                    db_files = get_databases()
                    db_files.append("EXIT")
                    delete_db = questionary.select("Which habit profile do you want to delete?",
                                                   choices=db_files, qmark="").ask()

                    if delete_db == "EXIT":
                        pass
                    else:
                        try:
                            confirmation = questionary.confirm(
                                "Do you really want to delete the profile \"" + delete_db + "\"?").ask()
                            if confirmation:
                                delete_db_ = delete_db + ".db"
                                import os
                                os.remove("habit profiles\\" + delete_db_)
                                print("The profile \"" + delete_db + "\" has been deleted.")
                        except PermissionError:
                            print(("The profile you are trying to delete is currently in use. "
                                   "Please switch to a different profile first."))

                elif profile_choice == "Load existing profile":
                    db_files = get_databases()
                    db_files.append("EXIT")
                    loaded_db = questionary.select("Which habit profile do you want to load?",
                                                   choices=db_files, qmark="").ask()
                    if loaded_db == "EXIT":
                        pass
                    else:
                        loaded_db_ = loaded_db + ".db"
                        db = get_db(name=loaded_db_)
                        print(f"The profile \"{loaded_db}\" has been loaded.")
                        break

                elif profile_choice == "Set default profile":
                    db_files = get_databases()
                    db_files.append("EXIT")
                    with open("config.json") as outfile:
                        config = json.load(outfile)
                    current_default_db = config["default_profile"]
                    default_db = questionary.select(("Which habit profile do you want to set as default?\n"
                                                     f" (The current default profile is \"{current_default_db}\")"),
                                                    choices=db_files, qmark="").ask()
                    if default_db == "EXIT":
                        pass
                    else:
                        config = {"default_profile": default_db}
                        with open("config.json", "w") as outfile:
                            json.dump(config, outfile)
                        print(f"The profile \"{default_db}\" has been set as the default profile. It is "
                              f"loaded into the Tracker when HabTrack is started.")

                elif profile_choice == "Create example profile":
                    databases = get_databases()
                    while True:
                        while True:
                            ex_db = questionary.text("Choose a name for the example profile: ").ask()
                            if ex_db in databases:
                                print("There is already a profile with this name. Try again with a different name.")
                            else:
                                break
                        while True:
                            chance_of_checkoff = questionary.text("Choose a probability (in %) for "
                                                                  "\"check-offs\": ").ask()
                            if not chance_of_checkoff.isdigit() or not 0 <= int(chance_of_checkoff) <= 100:
                                print(("Please choose a whole number between 0 and 100 for the probability (in %) of"
                                       " \"check-offs\"."))
                            else:
                                break
                        try:
                            ex_db_ = ex_db + ".db"
                            create_example_profile(name=ex_db_, chance_of_checkoff=int(chance_of_checkoff))
                            db = get_db(name=ex_db_)
                            print(f"The example profile \"{ex_db}\" has been created and loaded.")
                            break
                        except sqlite3.OperationalError:
                            print("The profile name must not contain any special characters. Please try again with "
                                  "a different profile name.")

                elif profile_choice == "EXIT":
                    break

        elif choice == "EXIT":
            break


if __name__ == '__main__':
    cli()
