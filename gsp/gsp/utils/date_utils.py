import datetime


def get_nth_previous_working_date(n: int, date: datetime.date = datetime.date.today()) -> datetime.date:
    """
    TODO: needs to include the leap years
    A function that returns the nth previous working date from the given date.
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

    account_for_future: bool = n < 0

    n += 2 * ((n + account_for_future) // 5)

    return date - datetime.timedelta(days=n)
