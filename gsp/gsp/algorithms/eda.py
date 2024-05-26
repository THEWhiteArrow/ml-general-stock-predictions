#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from typing import Dict, cast
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data import SCRAPED_STOCK_FILE_PATH
from sklearn.preprocessing import StandardScaler


# LOAD DATA

# In[ ]:


MAIN_INDEX = ["Date", "Area", "Name"]
SECONDARY_INDEX = ["Area", "Name"]

YEARS_BACK_TO_CONSIDER = 5

stocks = (
    pd.read_csv(
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
        index_col=MAIN_INDEX,
    )
    .sort_index()
    .loc[datetime.date.today() - pd.DateOffset(years=YEARS_BACK_TO_CONSIDER) :]
)

UNIQUE_AREAS = stocks.index.get_level_values("Area").unique()
stocks


# STANDARDIZE STOCKS CLOSE PRICES

# ***NOTICE***
# - all the stocks are standardized separately - this will allow
# to display the stocks on the same plot

# In[ ]:


scales_set: Dict[str, pd.DataFrame] = {}


def standardize_stock_group(group: pd.DataFrame) -> pd.DataFrame:
    scaler = StandardScaler()
    scaler.fit(group)

    stock_standardized = pd.DataFrame(
        data=cast(np.ndarray, scaler.transform(group)), columns=group.columns, index=group.index
    )
    stock_scales = pd.DataFrame(
        data=cast(np.ndarray, scaler.scale_).reshape(1, -1),
        columns=group.columns,
    )

    scales_set[group.index.get_level_values("Name")[0]] = stock_scales
    return stock_standardized


std_stocks = stocks.groupby(SECONDARY_INDEX, observed=False, group_keys=False).apply(standardize_stock_group)
std_stocks


# INVESTIGATE STOCKS AREA HOMOGENEITY

# In[ ]:


def plot_comparison_in_groups(group: pd.DataFrame):
    fig = plt.figure(figsize=(12, 6))
    ax = fig.gca()

    group.reset_index("Area")["Close"].unstack("Name").plot(
        title=cast(str, group.index.get_level_values("Area")[0]),
        ylabel="Close Price Standardized",
        xlabel="Date",
        grid=True,
        legend=True,
        ax=ax,
    )
    ax.legend(
        [
            f"{cast(str, line.get_label())} (scale: {scales_set[cast(str, line.get_label())]['Close'].values[0]:.2f})"
            for line in ax.get_lines()
        ]
    )

    plt.show()

    return group


std_stocks.groupby("Area", observed=True, group_keys=False).apply(plot_comparison_in_groups)


# INVESTIGATE STOCKS AREA AVERAGE

# In[ ]:


def plot_average_in_groups(group: pd.DataFrame):
    fig = plt.figure(figsize=(12, 6))
    ax = fig.gca()

    group.reset_index().groupby("Date")["Close"].mean().plot(
        title=f"Average Close Prices for {cast(str, group.index.get_level_values("Area")[0])}",
        ylabel="Close Price Standardized",
        xlabel="Date",
        legend=True,
        ax=ax,
    )
    plt.show()
    return group


std_stocks.groupby("Area", observed=True).apply(plot_average_in_groups)


# FURTHER DATA EXPLORATION

# In[ ]:


sns.heatmap(stocks.corr("spearman"), vmax=1, vmin=-1, center=0, annot=True)
plt.show()

