#!/usr/bin/env python
# coding: utf-8

# **IMPORTS**

# In[ ]:


import json
import datetime
import pandas as pd
from typing import List, Tuple, cast, Dict
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from sklearn.multioutput import RegressorChain
from sklearn.preprocessing import OneHotEncoder
from sklearn.calibration import LabelEncoder
from sklearn.metrics import mean_squared_log_error
from xgboost import XGBRegressor
import optuna
from gsp.utils.column_transformer_wrapper import ColumnTransformerWrapper
from gsp.utils.group_shifts import make_mw_in_groups, make_shift_in_groups
from gsp.utils.date_utils import get_nth_previous_working_date
from data import SCRAPED_STOCK_FILE_PATH, OUTPUT_DIR_PATH, save_output, load_output
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)

N_STEPS: int = 21
N_OPTIMIZE_TRIALS: int = -1  # --- NOTICE --- Negative value means no optimization
DAYS_BACK_TO_CONSIDER: int = 5 * 252
LABEL_FEATURES: List[str] = ["Year"]
CATEGORICAL_FEATURES: List[str] = ["DayOfWeek", "AreaCat"]
SHIFT_LIST: List[int] = [1, 2, 3]
MWM_LIST: List[int] = [5, 10, 15]
HYPER_PARAMS: Dict = {}


# **FUNCTIONS**

# In[ ]:


def root_mean_squared_log_error(y_true: pd.DataFrame, y_pred: pd.DataFrame) -> float:
    return cast(float, mean_squared_log_error(y_true, y_pred) ** 0.5)


def load_data() -> pd.DataFrame:
    return pd.read_csv(
        SCRAPED_STOCK_FILE_PATH,
        dtype={
            "Date": "period[D]",
            "Open": "float",
            "High": "float",
            "Low": "float",
            "Close": "float",
            "Volume": "int",
            "Area": "category",
            "Name": "category",
        },
    )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    periods = pd.date_range(
        start=df["Date"].min().to_timestamp().date(), end=df["Date"].max().to_timestamp().date(), freq="B"
    )
    periods_df = pd.DataFrame({"Date": periods}, dtype="period[D]")

    clean_data = (
        cast(
            pd.DataFrame,
            periods_df.set_index("Date")
            .join(df.set_index("Date"))
            .set_index("Name", append=True)
            .sort_index()
            .unstack("Name")
            .ffill()
            .bfill()  # --- NOTICE --- This is a fix so that the single problem approach works. It is not the best way to handle missing data.
            .stack("Name", future_stack=True),  # type: ignore
        )
        .reset_index()
        .dropna(subset=["Name"])
        .set_index(["Date", "Name"])
    )

    return clean_data


def engineer_features(
    df: pd.DataFrame,
    categorical_features: List[str] = [],
    shift_list: List[int] = [],
    mwm_list: List[int] = [],
    label_features: List[str] = [],
) -> pd.DataFrame:

    df = df.copy()

    cat_features_to_use: List[str] = [*categorical_features, *label_features]

    if "DayOfWeek" in cat_features_to_use:
        df["DayOfWeek"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).dayofweek

    if "Month" in cat_features_to_use:
        df["Month"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).month

    if "Year" in cat_features_to_use:
        df["Year"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).year

    if "WeekOfYear" in cat_features_to_use:
        df["WeekOfYear"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).week  # type: ignore

    if "DayOfMonth" in cat_features_to_use:
        df["DayOfMonth"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).day

    if "Quarter" in cat_features_to_use:
        df["Quarter"] = cast(pd.PeriodIndex, df.index.get_level_values("Date")).quarter

    if "AreaCat" in cat_features_to_use:
        df["AreaCat"] = df["Area"]

    grouped_lags: List[pd.DataFrame | pd.Series] = [
        make_shift_in_groups(df, groupby=["Name"], column="Close", shift=shift_list),
        make_mw_in_groups(df, groupby=["Name"], column="Close", window=mwm_list),
    ]

    df_grouped_lags = df.join(grouped_lags, how="left")

    return df_grouped_lags


def process_data(
    df: pd.DataFrame,
    n_steps: int,
    categorical_features: List[str],
    label_features: List[str] = [],
    days_back_to_consider: int | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    df = df.copy()

    """First date where all stocks have data"""
    first_all_valid_date: datetime.date = (
        cast(pd.Period, df.unstack("Name").dropna().first_valid_index()).to_timestamp().date()
    )

    latest_date: datetime.date = cast(pd.Period, df.index.get_level_values("Date").max()).to_timestamp().date()

    earliest_date: datetime.date = first_all_valid_date

    starting_date_to_consider: datetime.date | None = None

    if days_back_to_consider is not None:
        starting_date_to_consider = get_nth_previous_working_date(n=days_back_to_consider, date=latest_date)

    if starting_date_to_consider is not None and starting_date_to_consider < first_all_valid_date:
        logger.warning(
            f"WARNING: starting_date_to_consider ({starting_date_to_consider}) is before the first date where all stocks have data. Using {first_all_valid_date} instead."
        )
    elif starting_date_to_consider is not None:
        earliest_date = starting_date_to_consider

    logger.info(f"Earliest date: {earliest_date.isoformat()}")

    ctw = ColumnTransformerWrapper(
        transformers=[
            ("onehot", OneHotEncoder(drop="first"), categorical_features),
            ("label", LabelEncoder(), label_features),
        ],
        remainder="passthrough",
    )

    df_from_earliest = df.loc[earliest_date.isoformat() :]  # type: ignore
    X = ctw.fit_transform(df_from_earliest.drop(columns=["Adj Close", "Volume", "High", "Low", "Open", "Area"]))
    y = make_shift_in_groups(df, groupby=["Name"], column="Close", shift=[-i for i in range(1, n_steps + 1)])

    y, X = y.align(X.dropna(), axis=0, join="inner")

    return X, y


def split_data(
    X: pd.DataFrame,
    y: pd.DataFrame,
    n_steps: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """A function that splits the time series data into train and test sets in regards
    to the number of forecasting steps. It will test the model on the last 2*n_steps.

    Args:
        X (pd.DataFrame): Features dataframe
        y (pd.DataFrame): Target dataframe
        n_steps (int): Number of steps of the forecasting task

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: X_train, y_train, X_test, y_test
    """
    latest_date = cast(pd.Period, X.index.get_level_values("Date").max()).to_timestamp().date()
    test_end_date = get_nth_previous_working_date(n=n_steps, date=latest_date)
    test_start_date = get_nth_previous_working_date(n=2 * n_steps - 1, date=latest_date)
    train_end_date = get_nth_previous_working_date(n=2 * n_steps, date=latest_date)

    X_train = X.loc[: train_end_date.isoformat()]  # type: ignore
    y_train = y.loc[: train_end_date.isoformat()]  # type: ignore
    X_test = X.loc[test_start_date.isoformat() : test_end_date.isoformat()]  # type: ignore
    y_test = y.loc[test_start_date.isoformat() : test_end_date.isoformat()]  # type: ignore

    return X_train, y_train, X_test, y_test


def create_model(**hyper_params):
    model = RegressorChain(XGBRegressor(**hyper_params))

    return model


def convert_last_prediction_to_output(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    latest_date = cast(pd.Period, df.index.get_level_values("Date").max()).to_timestamp().date()

    y_latest = cast(pd.DataFrame, df.loc[latest_date.isoformat()]).rename(
        columns={
            f"Close_lead_{i}": get_nth_previous_working_date(n=-i, date=latest_date).isoformat()
            for i in range(1, len(df.columns) + 1)
        }
    )

    y_output = (
        y_latest.reset_index()
        .melt(id_vars=["Name"], var_name="Date", value_name="Close")
        .astype(
            {
                "Date": "period[D]",
                "Name": "category",
                "Close": "float",
            }
        )
        .set_index(["Date", "Name"])
    )

    return y_output


def solve(
    hyper_params: Dict,
    X: pd.DataFrame,
    y: pd.DataFrame,
    X_query: pd.DataFrame,
    single_problem_approach: bool = False,
) -> pd.DataFrame:

    y_pred = pd.DataFrame()
    if single_problem_approach is False:
        logger.info("Training and predicting for all stocks")
        model = create_model(**hyper_params)
        model.fit(X, y)
        y_pred = pd.DataFrame(model.predict(X_query), index=X_query.index, columns=y.columns)  # type: ignore
    else:
        unique_stock_names = X.index.get_level_values("Name").unique()
        for i, name in enumerate(unique_stock_names):
            logger.info(f"Training and predicting for {name} | {i + 1}/{len(unique_stock_names)}")
            X_single = cast(pd.DataFrame, X.loc[X.index.get_level_values("Name") == name])
            y_single = cast(pd.DataFrame, y.loc[y.index.get_level_values("Name") == name])
            X_query_single = cast(pd.DataFrame, X_query.loc[X_query.index.get_level_values("Name") == name])
            model = create_model(**hyper_params)
            model.fit(X_single, y_single)
            y_pred_single = pd.DataFrame(model.predict(X_query_single), index=X_query_single.index, columns=y_single.columns)  # type: ignore
            y_pred = pd.concat([y_pred, y_pred_single], axis=0)

    y_pred = y_pred.sort_index().clip(lower=0)
    logger.info("Prediction done")
    return y_pred


def optimize_with_optuna(
    X_train: pd.DataFrame,
    y_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.DataFrame,
    single_problem_approach: bool,
    n_optimize_trials: int,
) -> Tuple[float, Dict]:
    study = optuna.create_study(
        direction="minimize",
        study_name=f"optuna_optimization_{'single_approach' if single_problem_approach else "multi_approach"}",
    )

    def optuna_optimize_objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1200, step=50),  # Number of trees in the ensemble
            "max_depth": trial.suggest_int("max_depth", 3, 15),  # Maximum depth of each tree
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),  # Learning rate
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),  # Subsample ratio of the training instances
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree", 0.5, 1.0
            ),  # Subsample ratio of columns when constructing each tree
            "gamma": trial.suggest_float(
                "gamma", 0.01, 10.0, log=True
            ),  # Minimum loss reduction required to make a further partition on a leaf node of the tree
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 100.0, log=True),  # L1 regularization term on weights
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 100.0, log=True),  # L2 regularization term on weights
            "min_child_weight": trial.suggest_float(
                "min_child_weight", 1, 100, log=True
            ),  # Minimum sum of instance weight (hessian) needed in a child
        }

        y_pred = solve(
            hyper_params=params,
            X=X_train,
            y=y_train,
            X_query=X_test,
            single_problem_approach=single_problem_approach,
        )
        rmsle = root_mean_squared_log_error(y_test, y_pred)
        return rmsle

    study.optimize(optuna_optimize_objective, n_trials=n_optimize_trials)
    best_params = study.best_params
    best_rmsle = study.best_value

    return best_rmsle, best_params


# In[ ]:


def execute_test_run(
    n_steps: int,
    days_back_to_consider: int,
    categorical_features: List[str],
    label_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
    hyper_params: Dict = {},
    n_optimize_trials: int = -1,
    single_problem_approach: bool = False,
    combined: bool = False,
):

    stocks = load_data()
    clean = clean_data(stocks)
    features = engineer_features(
        clean, categorical_features, shift_list=shift_list, mwm_list=mwm_list, label_features=label_features
    )
    X, y = process_data(features, n_steps, categorical_features, days_back_to_consider=days_back_to_consider)
    X_train, y_train, X_test, y_test = split_data(X, y, n_steps)

    # --- Setup for the test run ---
    final_rmsle: float = 0.0
    final_y_pred: pd.DataFrame = pd.DataFrame()
    final_hyper_params: Dict = {}

    # --- Training and predicting ---
    if combined is False:
        y_default_pred = solve(
            hyper_params=hyper_params,
            X=X_train,
            y=y_train,
            X_query=X_test,
            single_problem_approach=single_problem_approach,
        )
    else:
        y_single_pred = solve(
            hyper_params=hyper_params,
            X=X_train,
            y=y_train,
            X_query=X_test,
            single_problem_approach=False,
        )
        y_multi_pred = solve(
            hyper_params=hyper_params,
            X=X_train,
            y=y_train,
            X_query=X_test,
            single_problem_approach=True,
        )

        y_default_pred = (y_single_pred + y_multi_pred) / 2

    rmsle_default = root_mean_squared_log_error(y_test, y_default_pred)

    final_rmsle = rmsle_default
    final_y_pred = y_default_pred
    final_hyper_params = hyper_params

    if n_optimize_trials > 0:
        optuna_rmsle, optuna_hyper_params = optimize_with_optuna(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            single_problem_approach=single_problem_approach,
            n_optimize_trials=n_optimize_trials,
        )

        if optuna_rmsle < final_rmsle:

            final_hyper_params = optuna_hyper_params
            final_rmsle = optuna_rmsle
            final_y_pred = solve(
                hyper_params=optuna_hyper_params,
                X=X_train,
                y=y_train,
                X_query=X_test,
                single_problem_approach=single_problem_approach,
            )

    y_output = convert_last_prediction_to_output(final_y_pred)
    return final_rmsle, y_output, final_hyper_params


def save_test_logs(
    rmsle: float,
    y_output: pd.DataFrame,
    hyper_params: Dict,
    single_problem_approach: bool,
    n_steps: int,
    days_back_to_consider: int,
    categorical_features: List[str],
    label_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
) -> None:
    test_history_log_df = load_output("test_history_log.csv")
    test_prediction_date = get_nth_previous_working_date(
        n=1, date=cast(pd.Period, y_output.index.get_level_values("Date").min()).to_timestamp().date()
    )
    current_input_df = pd.DataFrame(
        {
            "Version": [test_history_log_df.shape[0] + 1],
            "Created_Date": [datetime.date.today()],
            "Prediction_Date": [test_prediction_date],
            "RMSLE": [rmsle],
            "HyperParams": [hyper_params],
            "CategoricalFeatures": [categorical_features],
            "LabelFeatures": [label_features],
            "NSteps": [n_steps],
            "Shift_list": [shift_list],
            "MWM_list": [mwm_list],
            "Phase": [1],
            "DaysBackToConsider": [days_back_to_consider],
            "SingleProblemApproach": [single_problem_approach],
        },
    )

    test_history_log_df = pd.concat([test_history_log_df, current_input_df], axis=0)
    test_history_log_df = test_history_log_df.set_index("Version")
    save_output(test_history_log_df, "test_history_log.csv")


def display_test_predictions(
    y_output: pd.DataFrame,
    categorical_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
    label_features: List[str],
    days_back_to_display: int,
    columns_n: int,
) -> Figure:
    # --- Get the correct data to display ---
    stocks = load_data()
    clean = clean_data(stocks)
    features = engineer_features(
        clean, categorical_features, shift_list=shift_list, mwm_list=mwm_list, label_features=label_features
    )

    unique_names = y_output.index.get_level_values("Name").unique()
    unique_names_n = len(unique_names)

    rows_n = -(-unique_names_n // columns_n)

    fig, axs = plt.subplots(rows_n, columns_n, figsize=(15, 6 * rows_n))

    for i, name in enumerate(unique_names):

        axs[i // columns_n, i % columns_n].set_title(f"Close for {name}")

        cast(pd.DataFrame, features[features.index.get_level_values("Name") == name]).reset_index("Name")["Close"].tail(
            days_back_to_display
        ).plot(label=f"Close for {name}", ax=axs[i // columns_n, i % columns_n])

        cast(pd.DataFrame, y_output[y_output.index.get_level_values("Name") == name]).reset_index("Name")["Close"].plot(
            label=f"Predicted Close for {name}", ax=axs[i // columns_n, i % columns_n]
        )

    plt.show()

    return fig


def execute_real_run(
    n_steps: int,
    days_back_to_consider: int,
    categorical_features: List[str],
    label_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
    hyper_params: Dict = {},
    single_problem_approach: bool = False,
) -> pd.DataFrame:

    stocks = load_data()
    clean = clean_data(stocks)
    features = engineer_features(
        clean, categorical_features, shift_list=shift_list, mwm_list=mwm_list, label_features=label_features
    )
    X, y = process_data(features, n_steps, categorical_features, days_back_to_consider=days_back_to_consider)
    X_train, y_train = X.align(y.dropna(), axis=0, join="inner")
    X_query = X.copy(deep=True)

    y_pred = solve(
        hyper_params=hyper_params,
        X=X_train,
        y=y_train,
        X_query=X_query,
        single_problem_approach=single_problem_approach,
    )

    y_output = convert_last_prediction_to_output(y_pred)

    return y_output


# **TEST EXECUTION**

# In[ ]:


def test_prediction(
    name: str,
    n_steps: int,
    days_back_to_consider: int,
    categorical_features: List[str],
    label_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
    hyper_params: Dict,
    single_problem_approach: bool,
    n_optimize_trials: int,
    save_image: bool,
    combined: bool,
) -> Tuple[float, pd.DataFrame, Dict]:

    rmsle, y_output, best_hyper_params = execute_test_run(
        n_steps=n_steps,
        days_back_to_consider=days_back_to_consider,
        categorical_features=categorical_features,
        label_features=label_features,
        shift_list=shift_list,
        mwm_list=mwm_list,
        hyper_params=hyper_params,
        n_optimize_trials=n_optimize_trials,
        single_problem_approach=single_problem_approach,
        combined=combined,
    )

    save_test_logs(
        rmsle=rmsle,
        y_output=y_output,
        hyper_params=best_hyper_params,
        single_problem_approach=single_problem_approach,
        n_steps=n_steps,
        days_back_to_consider=days_back_to_consider,
        categorical_features=categorical_features,
        label_features=label_features,
        shift_list=shift_list,
        mwm_list=mwm_list,
    )

    fig = display_test_predictions(
        y_output=y_output,
        categorical_features=categorical_features,
        shift_list=shift_list,
        mwm_list=mwm_list,
        label_features=label_features,
        days_back_to_display=125,
        columns_n=3,
    )

    test_prediction_date = get_nth_previous_working_date(
        n=1, date=cast(pd.Period, y_output.index.get_level_values("Date").min()).to_timestamp().date()
    )
    if save_image is True:
        fig.savefig(f"{OUTPUT_DIR_PATH}/test_prediction_{name}_{test_prediction_date}.png")

    return rmsle, y_output, best_hyper_params


# **GENERATE PREDICTION**

# In[ ]:


def generate_prediction(
    name: str,
    n_steps: int,
    days_back_to_consider: int,
    categorical_features: List[str],
    label_features: List[str],
    shift_list: List[int],
    mwm_list: List[int],
    hyper_params: Dict,
    single_problem_approach: bool,
) -> datetime.date:
    y_real_output = execute_real_run(
        n_steps=n_steps,
        days_back_to_consider=days_back_to_consider,
        categorical_features=categorical_features,
        label_features=label_features,
        shift_list=shift_list,
        mwm_list=mwm_list,
        hyper_params=hyper_params,
        single_problem_approach=single_problem_approach,
    )

    real_prediction_date = get_nth_previous_working_date(
        n=1, date=cast(pd.Period, y_real_output.index.get_level_values("Date").min()).to_timestamp().date()
    )

    generation_df = pd.DataFrame(
        {
            "PredictionDate": [real_prediction_date.isoformat()],
            "CreatedTimestamp": [datetime.datetime.now(datetime.UTC)],
            "CategoricalFeatures": [json.dumps(categorical_features)],
            "LabelFeatures": [json.dumps(label_features)],
            "ShiftList": [json.dumps(shift_list)],
            "MWMList": [json.dumps(mwm_list)],
            "DaysBackToConsider": [days_back_to_consider],
            "NSteps": [n_steps],
            "Name": [name],
            "HyperParams": [json.dumps(hyper_params)],
        }
    ).set_index(["PredictionDate", "Name"])

    save_output(y_real_output, f"prediction_{real_prediction_date.isoformat()}.csv")
    save_output(generation_df, f"generation_{real_prediction_date.isoformat()}.csv")

    return real_prediction_date


# In[ ]:


# generate_prediction(
#     name="default_multi_approach",
#     n_steps=N_STEPS,
#     days_back_to_consider=DAYS_BACK_TO_CONSIDER,
#     categorical_features=CATEGORICAL_FEATURES,
#     label_features=LABEL_FEATURES,
#     shift_list=SHIFT_LIST,
#     mwm_list=MWM_LIST,
#     hyper_params=HYPER_PARAMS,
#     single_problem_approach=False,
# )

