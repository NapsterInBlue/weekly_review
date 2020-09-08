from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from itertools import cycle, islice

import pandas as pd


FIRST_DAY = "2016-07-27"  # arbitrary
INTRO_PATH = "./config/intro.txt"
HAPPINESS_PATH = "./config/happy.txt"
REMINDER_PATH = "./config/reminder.txt"
CSV_PATH = "./config/weekly_review.csv"


def spread_data():
    """
    If there are a gaggle of things that occur on an every-two-week
    basis, I don't want there to only be light and avalanche weeks.

    This counts groups off by their week frequency and allocates
    more-or-less evenly
    """
    df = pd.read_csv(CSV_PATH)
    df['Group'] = df['Group'].str.strip()

    for freq, group in df.groupby("WeekFrq"):
        if freq == 1:
            countoff = [0] * len(group)
        else:
            # e.g. 3 wk freq -> 0, 1, 2, 0, 1, 2, 0, 1, 2, ...
            countoff = list(islice(cycle(range(0, freq)), len(group)))

        df.loc[group.index, "Offset"] = pd.Series(countoff, index=group.index)

    df = df.sort_values(by=["Group", "Title"])

    df.to_csv(CSV_PATH, index=False)


def _print_from_txt(fpath: str, with_stops=False):
    """
    Print the text from a given fpath.

    `with_stops` enforces uncaptured press of Enter key before
    progressing to next line
    """

    print("\n")

    with open(fpath) as f:
        if with_stops:
            for line in f:
                input(line)
        else:
            print(f.read())

    print("\n" * 2)


def print_boilerplate():
    """
    Chain together the last 3 functions for consistent print before
    print_review_items()
    """
    _print_from_txt(INTRO_PATH, with_stops=True)
    _print_from_txt(HAPPINESS_PATH, with_stops=False)
    input()
    _print_from_txt(REMINDER_PATH, with_stops=False)


def get_this_weeks_monday():
    """
    Uses today's date to find the date of this week's Monday
    """
    today = datetime.today()
    if today.weekday() != 0:
        next_monday = today + relativedelta(weekday=0)
        this_monday = next_monday - timedelta(days=7)
    else:
        this_monday = today()

    return this_monday


def get_week_diff() -> int:
    """
    The week-offset mechanic is powered by calculating the number of
    weeks since the (arbitrary) original date, then some mod division
    magic
    """
    day_0 = parse(FIRST_DAY)
    this_monday = get_this_weeks_monday()
    week_diff = int((this_monday - day_0).days / 7)

    return week_diff


def print_review_items():
    """
    Scans through weekly_review.csv and builds a dictionary
    of category: item if the appropriate date criteria is met.

    A note on dates:
        The `offset` below checks against mod division of
        an arbitrarily-large `week_diff`, mod-divided by the `week_freq`,
        found in the .csv.

        `offset` will always yield a value in [0, n-1] for week offset, `n`,
        by design of `spread_data()` above

        Similarly, `todays_offset_group` will always yield a value in [0, n-1]
        by rules of mod division.
    """
    week_diff = get_week_diff()

    with open(CSV_PATH) as f:
        items = {}
        f.readline()  # skip header

        for line in f.readlines():
            group, title, week_freq, offset = line.strip().split(",")

            offset = int(float(offset))  # '0.0' -> 0

            todays_offset_group = week_diff % int(week_freq)

            if todays_offset_group == offset:
                if group in items:
                    items[group].append(title)
                else:
                    items[group] = [title]

    for category in items:
        print("\t" * 5 + category + "\n")
        for item in items[category]:
            print(item)
            input()
        print("___")
        input()
