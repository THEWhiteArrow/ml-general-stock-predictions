from dataclasses import dataclass
from typing import Any, List, Literal, Tuple, TypeAlias, cast
import datetime
import pandas as pd
from sklearn.compose import ColumnTransformer

MOVING_WINDOW_AGGREGATORS_ALIAS: TypeAlias = Literal["mean", "sum", "median", "std", "var", "min", "max"]


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
        df.groupby(groupby, observed=True, group_keys=False)
        .apply(create_shifted_columns, include_groups=False)
        .sort_index(),
    )

    return shifted_df


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
        df.groupby(groupby, observed=True, group_keys=False)
        .apply(create_mw_columns, include_groups=False)
        .sort_index(),
    )


def get_most_recent_working_date(date: datetime.date = datetime.date.today()) -> datetime.date:
    if date.weekday() == 5:
        return date - datetime.timedelta(days=1)
    elif date.weekday() == 6:
        return date - datetime.timedelta(days=2)
    return date


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


def show(*args):
    """A function that displays the arguments in a Jupyter notebook or prints them in a console depending on the environment."""
    try:
        from IPython.display import display

        display(*args)
    except ImportError:
        print(*args)


def get_all_missing_stock_names(stocks: pd.DataFrame, starting_date: datetime.date) -> List[str]:
    """A function that returns the list of stocks that have missing values in the given DataFrame.

    Args:
        stocks (pd.DataFrame): Stocks hitorical data
        starting_date (datetime.date): The starting date to check for missing values

    Returns:
        List[str]: List of stocks that have missing values
    """
    return cast(
        List[str],
        stocks.copy()
        .set_index(["Date", "Name"])
        .unstack("Name")
        .ffill()
        .stack("Name", future_stack=True)  # type: ignore
        .reset_index("Name")
        .loc[starting_date.isoformat() :]  # type: ignore
        .groupby("Date", group_keys=False)
        .apply(lambda r: r["Name"][r.isna().any(axis=1)].to_list())
        .iloc[0],
    )


def get_minimal_stocks_existence_date(stocks: pd.DataFrame) -> datetime.date:
    """A function that returns the minimal starting date for all stocks in the given DataFrame.

    Args:
        stocks (pd.DataFrame): Stocks hitorical data

    Returns:
        datetime.date: Minimal starting date for all stocks
    """
    return (
        cast(pd.Period, stocks.copy()[["Date"]].reset_index().groupby("Date").count().idxmax().iloc[0])
        .to_timestamp()
        .date()
    )


@dataclass
class ColumnTransformerWrapper:
    transformers: List[Tuple[str, Any, List[str]]]
    remainder: Literal["drop", "passthrough"] = "passthrough"

    def fit_transform(self, X: pd.DataFrame, y: Any | None = None) -> pd.DataFrame:  # type: ignore
        ct = ColumnTransformer(self.transformers, remainder=self.remainder)

        return pd.DataFrame(
            ct.fit_transform(X, y),  # type: ignore
            index=X.index,
            columns=[col.replace("remainder__", "") for col in ct.get_feature_names_out()],
        )
