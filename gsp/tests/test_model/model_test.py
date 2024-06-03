import pytest
import pandas as pd
from gsp.model.model import (
    root_mean_squared_log_error,
    clean_data,
    # engineer_features,
    # process_data,
    # split_data,
    # create_model,
)


def test_root_mean_squared_log_error_zero_diff():
    y_true = pd.DataFrame([1, 2, 3])
    y_pred = pd.DataFrame([1, 2, 3])
    assert root_mean_squared_log_error(y_true, y_pred) == 0.0


def test_root_mean_squared_log_error_non_zero_diff():
    y_true = pd.DataFrame([5, 5, 5])
    y_pred = pd.DataFrame([25, 25, 25])
    assert root_mean_squared_log_error(y_true, y_pred) != 0


def test_root_mean_squared_log_error_with_negative_values_throws_error():
    y_true = pd.DataFrame([5, 5, 5])
    y_pred = pd.DataFrame([-25, -25, -25])

    try:
        root_mean_squared_log_error(y_true, y_pred)
        pytest.fail("Should have thrown an error")
    except ValueError:
        assert True


def test_clean_data_no_missing_business_days():
    # --- SETUP ---
    monday = pd.Period("2024-05-20")
    tuesday = pd.Period("2024-05-21")
    thursday = pd.Period("2024-05-23")
    friday = pd.Period("2024-05-24")

    wednesday = pd.Period("2024-05-22")

    data = pd.DataFrame(
        {
            "date": [monday, tuesday, thursday, friday, monday, tuesday, thursday, friday],
            "symbol": ["AAPL", "AAPL", "AAPL", "AAPL", "GOOGL", "GOOGL", "GOOGL", "GOOGL"],
            "close": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        }
    )

    # --- ACT ---
    cleaned_data = clean_data(data)
    cleaned_data_dates = cleaned_data.index.get_level_values("date").unique()
    assert wednesday in cleaned_data_dates
