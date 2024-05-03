import os
from typing import Dict, List, Literal, TypeAlias

SCRAPED_DIR: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scraped")
SCRAPED_STOCK_FILE_PATH: str = os.path.join(SCRAPED_DIR, "stocks.csv")
SCRAPED_TRADED_STOCK_LIST_FILE_PATH: str = os.path.join(SCRAPED_DIR, "traded_stocks.csv")

SETUP_STOCK_FILE_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "setup", "stocks_setup.json")
SETUP_STOCK_COMPANY_ALIAS: TypeAlias = Dict[Literal["company_name", "stock_id"], str]
SETUP_STOCK_ALIAS: TypeAlias = Dict[str, List[SETUP_STOCK_COMPANY_ALIAS]]
