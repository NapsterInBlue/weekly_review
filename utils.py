from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from itertools import cycle, islice

import pandas as pd

from conf import HAPPINESS_FPATH, FIRST_DAY


def spread_data():
    """
    If there are a gaggle of things that occur on an every-two-week
    basis, I don't want there to only be light and avalanche weeks.

    This counts groups off by their week frequency and allocates
    more-or-less evenly
    """
    csv_path = "weekly_review.csv"
    df = pd.read_csv(csv_path)

    for freq, group in df.groupby("WeekFrq"):
        # e.g. 3 wk freq -> 0, 1, 2, 0, 1, 2, 0, 1, 2, ...
        countoff = list(islice(cycle([0, freq - 1]), len(group)))
        df.loc[group.index, "Offset"] = pd.Series(countoff, index=group.index)

    df = df.sort_values(by=["Group", "Title"])

    df.to_csv(csv_path, index=False)


def _print_intro():
    """
    Simple print statements, separated by input() calls so user has
    to think about each point
    """
    print("\n" * 3)

    print("Before you do anything:\n")
    input("Calendar out your personal time.")
    input("Calendar out your work time.")
    input("Read the last couple entries in the ol' journal")
    input("What are you happy about this last week?\n\n")


def _print_happiness():
    """
    Print the contents of the file conf.HAPPINESS_PATH points to
    """
    with open(HAPPINESS_FPATH) as f:
        print(f.read())

    print("\n" * 3)


def _print_reminder():
    """
    More print/input() calls before the meat of the script kicks off
    """
    print("Great. Now a couple notes:\n")
    print("Schedule all of your texts and messages.")
    input(
        "This is time for reflection,"
        " not struggling to feel like you're accomplishing things."
    )

    print("\n" * 2)


def print_boilerplate():
    """
    Chain together the last 3 functions for consistent print before
    print_review_items()
    """
    _print_intro()
    _print_happiness()
    _print_reminder()


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

    with open("weekly_review.csv") as f:
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
