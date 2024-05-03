from typing import List, Literal, TypeAlias, cast
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
