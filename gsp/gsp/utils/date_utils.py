import datetime


def get_nth_previous_working_date(n: int, date: datetime.date = datetime.date.today()) -> datetime.date:
    """
    A function that returns the nth previous working date from the given date.
    If the given date is a weekend it defaults the current date to the last working day (friday).
    Args:
        n (int): number of working days to go back
        today (datetime.date, optional): day from which the working days should be substracted. Defaults to datetime.date.today().

    Returns:
        datetime.date: the nth working day before the given date

    Example:
        >>> get_nth_previous_working_date(7, datetime.date(2024, 5, 2))
        datetime.date(2024, 4, 23)
    """
    if date.weekday() == 5:
        date = date - datetime.timedelta(days=1)
    elif date.weekday() == 6:
        date = date - datetime.timedelta(days=2)
    else:
        added_days = 4 - date.weekday()
        n += added_days
        date = date + datetime.timedelta(days=added_days)

    # --- NOTE ---
    """
    Funny enough, the logic is the same for both past and future dates.
    It is needed to add 2 days for each week difference since we only want to consider business (week) days.
    In case of past dates we need to add 2 days after each 5 days has passed because we start the data with a friday.
    In case of future dates we need to add -2 days after each 5 days starting at -2 already because since the initial day to which
    the date was moved is friday then any change will result in moving the days by -2 step (2 forward).
    Additionally since division is always rounded down we can use the // and it will by default set -1 for negative values.
    Example:
    1 // 5 = 0
    -1 // 5 = -1
    And this is the bahaviour that we want.
    """
    n += 2 * (n // 5)

    return date - datetime.timedelta(days=n)
