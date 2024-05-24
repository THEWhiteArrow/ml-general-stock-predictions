import pandas as pd
from gsp.utils.group_shifts import make_mw_in_groups, make_shift_in_groups


def test_make_shift_in_groups_single_index():
    # --- SETUP ---
    df = pd.DataFrame(
        {
            "group": ["a", "a", "a", "b", "b", "b"],
            "value2": [7, 8, 9, 10, 11, 12],
            "value1": [1, 2, 3, 4, 5, 6],
        },
    ).set_index(["group"])

    # --- ACT ---
    df["shifted"] = make_shift_in_groups(
        df=df,
        groupby=["group"],
        column="value1",
        shift=1,
    )

    # --- ASSERT ---
    assert pd.isna(df[df.index == "a"]["shifted"][0])
    assert df[df.index == "a"]["shifted"][1] == 1
    assert df[df.index == "a"]["shifted"][2] == 2


def test_make_shift_in_groups_multi_index():
    # --- SETUP ---
    df = pd.DataFrame(
        {
            "group": ["a", "a", "a", "b", "b", "b"],
            "value2": [7, 8, 9, 10, 11, 12],
            "value1": [1, 2, 3, 4, 5, 6],
        },
    ).set_index(["group", "value2"])

    # --- ACT ---
    df["shifted"] = make_shift_in_groups(
        df=df,
        groupby=["group"],
        column="value1",
        shift=1,
    )

    # --- ASSERT ---
    assert pd.isna(df[df.index.get_level_values("group") == "a"]["shifted"][0])
    assert df[df.index.get_level_values("group") == "a"]["shifted"][1] == 1
    assert df[df.index.get_level_values("group") == "a"]["shifted"][2] == 2
    assert df.index.nlevels == 2
    assert df.index.names == ["group", "value2"]


def test_make_mw_in_groups_single_index():
    # --- SETUP ---
    df = pd.DataFrame(
        {
            "group": ["a", "a", "a", "a", "b", "b", "b"],
            "value2": [7, 8, 9, 9.5, 10, 11, 12],
            "value1": [1, 2, 3, 3, 4, 5, 6],
        },
    ).set_index(["group"])

    # --- ACT ---
    df["shifted"] = make_mw_in_groups(
        df=df,
        groupby=["group"],
        column="value1",
        window=2,
        min_periods=2,
    )

    # --- NOTICE ---
    """Make moving window in groups function is supposed to give the mean of the last n previous days.
    It should not include the current day in the mean calculation, because it would provide look-ahead bias.
    """

    # --- ASSERT ---
    assert pd.isna(df[df.index == "a"]["shifted"][0])
    assert pd.isna(df[df.index == "a"]["shifted"][1])
    assert df[df.index == "a"]["shifted"][2] == 1.5
    assert df[df.index == "a"]["shifted"][3] == 2.5
