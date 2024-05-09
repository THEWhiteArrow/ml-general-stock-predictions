import os
from typing import Dict, List, Literal, TypeAlias
import pandas as pd

SCRAPED_DIR_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scraped")
SCRAPED_STOCK_FILE_PATH: str = os.path.join(SCRAPED_DIR_PATH, "stocks.csv")
SCRAPED_TRADED_STOCK_LIST_FILE_PATH: str = os.path.join(SCRAPED_DIR_PATH, "traded_stocks.csv")

SETUP_STOCK_FILE_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "setup", "stocks_setup.json")
SETUP_STOCK_COMPANY_ALIAS: TypeAlias = Dict[Literal["company_name", "stock_id"], str]
SETUP_STOCK_ALIAS: TypeAlias = Dict[str, List[SETUP_STOCK_COMPANY_ALIAS]]

OUTPUT_DIR_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "output")


def save_output(df: pd.DataFrame, file_name: str) -> None:
    df.to_csv(os.path.join(OUTPUT_DIR_PATH, file_name), index=False)


def load_output(file_name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(OUTPUT_DIR_PATH, file_name))
