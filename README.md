# HabTrack
HabTrack is a habit tracker app that was built with Python as part of a further 
education course with the topic "Object-Oriented and Functional Programming". 

The aim of this app is to aid users in the challenging process of acquiring new good habits.

## Main features
- Create habits with a specified task and "daily" or "weekly" periodicity. Examples:
  - "Not using the phone in the morning" (daily)
  - "Going to the gym two times a week" (weekly)
- The main user responsibility is to "check-off" the habit task daily or weekly (depending on 
the chosen periodicity) whenever the user completed a habit task in real life. 
If the user misses a check-off, the user is said to "break the habit".
The goal is to maximize the run streak of check-offs.
- Analyze the tracking progress:
  - Return the tracking data for a given habit
  - Return the longest run streak for a given habit
  - Return the longest run streak of all defined habits
  - And more...
- Create multiple habit profiles, each having its own set of habits. An example
use case could be that each family member or friend has their own profile with their
own habits. This also enables to compete against each other in achieving the longest run streak.
 

## Installation
````shell
pip install -r requirements.txt
````

## Usage
Run
```shell
python main.py
```
and use the arrow keys to navigate through the app menus. 

In "Tracker" you can create new habits, delete habits, check-off habit tasks and analyze habits. 
The currently loaded profile is shown at the top.

In "Profile" you can create new profiles, delete profiles, load a profile into the "Tracker" and set
a profile as the default profile. The default profile will be loaded into the "Tracker" when the app is started.
Additionally, you can create "example" profiles. For more information on that, read the next section "Tests".


## Tests
The main functionalities of the app can be tested with the included unit test suite. 

Run
````shell
pytest .
````
to start the unit testing. 

Additionally, the provided "example" profile with five predefined
habits, each with four weeks of tracking data, can be loaded into the "Tracker" 
and can be used to test the main functionalities and to get a feel for the app.

You can also create your own example profiles in the "Profile" menu. The profiles
created with "Create example profile" come with five predefined habits and four weeks of randomized 
tracking data for each habit. 
The amount of check-offs in the randomized tracking data depends on the entered probability 
for check-offs in %. E.g. if you choose 75%, then for every period (day or week) there is a 
75% chance that the task will be checked-off.

