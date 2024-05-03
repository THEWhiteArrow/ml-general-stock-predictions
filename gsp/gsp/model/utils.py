from typing import List, Literal, TypeAlias, cast
import datetime
import pandas as pd


MOVING_WINDOW_AGGREGATORS_ALIAS: TypeAlias = Literal["mean", "sum", "median", "std", "var"]


def make_mw_in_groups(
    df: pd.DataFrame,
    groupby: List[str] = [],
    column: str = "",
    window: List[int] | int = 30,
    center: List[bool] | bool = False,
    min_periods: List[int] | int = 1,
    aggregator: List[MOVING_WINDOW_AGGREGATORS_ALIAS] | MOVING_WINDOW_AGGREGATORS_ALIAS = "mean",
    name: str | None = None,
) -> pd.DataFrame:
    df = df.copy(deep=True)
    if name is None:
        name = column

    if isinstance(window, int):
        window = [window]

    window = list(filter(lambda x: x != 0, window))
    if len(window) == 0:
        raise ValueError("Window value must be non-zero!")
    if isinstance(center, bool):
        center = [center] * len(window)
    if isinstance(min_periods, int):
        min_periods = [min_periods] * len(window)
    if isinstance(aggregator, str):
        aggregator = cast(List[MOVING_WINDOW_AGGREGATORS_ALIAS], [aggregator]) * len(window)

    def create_mw_columns(group):
        ma_group = pd.DataFrame(index=group.index)
        for index, val in enumerate(window):
            type_name = "lag" if val > 0 else "lead"
            if val < 0:
                ma_group[f"{name}_{type_name}_{aggregator[index]}_{-val}"] = (
                    group[column]
                    .rolling(window=-val, center=center[index], min_periods=min_periods[index])
                    .aggregate(aggregator[index])
                    .shift(val)
                )
            else:
                ma_group[f"{name}_{type_name}_{aggregator[index]}_{val}"] = (
                    group[column]
                    .shift(1)
                    .rolling(window=val, center=center[index], min_periods=min_periods[index])
                    .aggregate(aggregator[index])
                )

        return ma_group

    return cast(
        pd.DataFrame,
        df.reset_index(groupby)
        .groupby(groupby, observed=True)
        .apply(create_mw_columns, include_groups=False)
        .reset_index(groupby)
        .set_index(groupby, append=True)
        .sort_index(),
    )


def make_shift_in_groups(
    df: pd.DataFrame,
    groupby: List[str] = [],
    column: str = "",
    shift: List[int] | int = 1,
    name: str | None = None,
) -> pd.DataFrame:
    df = df.copy(deep=True)
    if name is None:
        name = column

    if isinstance(shift, int):
        shift = [shift]

    shift = list(filter(lambda el: el != 0, shift))

    if len(shift) == 0:
        raise ValueError("Shift value must be non-zero!")

    def create_shifted_columns(group):
        shifted_group = pd.DataFrame(index=group.index)
        for val in shift:

            shifted_group[f"{name}_{'lead' if val < 0 else 'lag'}_{abs(val)}"] = group[column].shift(val)

        return shifted_group

    shifted_df = cast(
        pd.DataFrame,
        df.reset_index(groupby)
        .groupby(groupby, observed=True)
        .apply(create_shifted_columns, include_groups=False)
        .reset_index(groupby)
        .set_index(groupby, append=True)
        .sort_index(),
    )

    return shifted_df


def get_most_recent_working_date(date: datetime.date = datetime.date.today()) -> datetime.date:
    if date.weekday() == 5:
        return date - datetime.timedelta(days=1)
    elif date.weekday() == 6:
        return date - datetime.timedelta(days=2)
    return date


def get_nth_previous_working_date(n: int, date: datetime.date = datetime.date.today()) -> datetime.date:
    """A function that returns the nth previous working date from the given date.

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


def show(*args):
    """A function that displays the arguments in a Jupyter notebook or prints them in a console depending on the environment."""
    try:
        from IPython.display import display

        display(*args)
    except ImportError:
        print(*args)
